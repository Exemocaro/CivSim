"""Character — a nation's leader with martial, prosperity, and vitality traits."""

from __future__ import annotations

import random
import logging

from civsim.settings import (
    AGE_PROBABILITIES_PAR,
    BASE_DEATH_VALUE,
    VITALITY_DEATH_BONUS,
    VITALITY_DEATH_PENALTY,
)
from civsim.names.names import name_gen

logger = logging.getLogger(__name__)


class Character:
    _global_id: int = 1

    def __init__(
        self,
        name: str,
        age: int,
        gender: str,
        martial: int,
        prosperity: int,
        vitality: int,
    ) -> None:
        self.id = Character._global_id
        self.name = name
        self.age = age
        self.gender = gender
        self.martial = martial          # combat bonus when attacking/defending
        self.prosperity = prosperity    # reduces resource rot, boosts money income
        self.vitality = vitality        # influences lifespan
        self.probability_of_dying: int = 0

        self.title = "King" if gender == "m" else "Queen"
        self.representation = "" if name == "" else f"{self.title} {name}"

        Character._global_id += 1

    # ------------------------------------------------------------------
    # Factory methods
    # ------------------------------------------------------------------

    @staticmethod
    def get_character(name: str, age: int, gender: str, martial: int, prosperity: int, vitality: int) -> Character:
        """Create a character with explicit stats."""
        return Character(name, age, gender, martial, prosperity, vitality)

    @staticmethod
    def get_random_character() -> Character:
        """Create a character with randomised stats."""
        gender = random.choice(["f", "m"])
        age = random.randint(18, 39)
        return Character(
            name_gen(gender),
            age,
            gender,
            random.randint(1, 10),
            random.randint(1, 10),
            random.randint(1, 10),
        )

    @staticmethod
    def get_successor(parent: Character) -> Character:
        """Create an heir with stats close to the parent's."""
        new_age = 17 if parent.age < 35 else random.randint(17, parent.age - 17)
        gender = random.choice(["f", "m"])

        def bounded_stat(base: int) -> int:
            candidates = [base - 2, base - 1, base, base + 1, base + 2]
            valid = [v for v in candidates if v > 0]
            return random.choice(valid) if valid else 1

        return Character(
            name_gen(gender),
            new_age,
            gender,
            bounded_stat(parent.martial),
            bounded_stat(parent.prosperity),
            bounded_stat(parent.vitality),
        )

    # ------------------------------------------------------------------
    # Ageing / death
    # ------------------------------------------------------------------

    def update(self) -> Character:
        """Age this character by one year.  Returns the character, or their
        successor if they die.
        """
        self.age += 1
        self.probability_of_dying = 0

        for age_threshold, death_prob in AGE_PROBABILITIES_PAR:
            if self.age > age_threshold:
                self.probability_of_dying = death_prob
                break

        self.probability_of_dying += BASE_DEATH_VALUE

        # Vitality modifies death chance
        if (self.vitality + 2) * 10 > self.age:
            self.probability_of_dying += VITALITY_DEATH_PENALTY
        else:
            self.probability_of_dying -= VITALITY_DEATH_BONUS

        if random.randint(1, 1000) <= self.probability_of_dying:
            logger.info("Leader %s (age %d) has died.", self.name, self.age)
            return Character.get_successor(self)
        return self

    # ------------------------------------------------------------------
    # Info helpers
    # ------------------------------------------------------------------

    def get_values(self) -> str:
        if not self.name:
            return ""
        return f"Age:{self.age} M:{self.martial} P:{self.prosperity} V:{self.vitality}"

    def get_info(self) -> list[str]:
        return [self.get_values()]

    def print_info(self) -> None:
        for line in self.get_info():
            print(line)

    def __repr__(self) -> str:
        return f"Character({self.name!r}, age={self.age})"
