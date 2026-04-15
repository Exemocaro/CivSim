"""Nation personality — drives AI behaviour (expansion vs. development)."""

from __future__ import annotations

from civsim.settings import BASE_CONQUER_COST, BASE_DEV_COST


class Personality:
    def __init__(
        self,
        name: str,
        phase: str,
        influence_cost_to_dev: float,
        influence_cost_to_conquer: float,
    ) -> None:
        self.name = name
        self.phase = phase
        self.influence_cost_to_dev = influence_cost_to_dev
        self.influence_cost_to_conquer = influence_cost_to_conquer
        self.max_wars: int = 0
        self.update_values()

    # ------------------------------------------------------------------
    # Cost updates (called whenever phase changes)
    # ------------------------------------------------------------------

    def update_influence_to_conquer(self) -> None:
        if self.phase == "aggressively-expanding":
            self.influence_cost_to_conquer = round(BASE_CONQUER_COST / 2, 2)
        elif self.phase == "peacefully-expanding":
            self.influence_cost_to_conquer = round(BASE_CONQUER_COST, 2)
        elif self.phase == "developing":
            self.influence_cost_to_conquer = round(BASE_CONQUER_COST * 2, 2)

    def update_influence_to_dev(self) -> None:
        if self.phase == "developing":
            self.influence_cost_to_dev = round(BASE_DEV_COST / 2, 2)
        elif self.phase == "peacefully-expanding":
            self.influence_cost_to_dev = round(BASE_DEV_COST, 2)
        elif self.phase == "aggressively-expanding":
            self.influence_cost_to_dev = round(BASE_DEV_COST * 2, 2)

    def update_values(self) -> None:
        self.update_influence_to_dev()
        self.update_influence_to_conquer()

    def __repr__(self) -> str:
        return f"Personality({self.name!r}, phase={self.phase!r})"


# ---------------------------------------------------------------------------
# Pool of personalities that nations are randomly assigned on creation.
# Three distinct starting phases ensures variety from turn 1.
# (Costs are immediately recalculated by update_values, so initial values here
# don't matter — but we pass the base constants for clarity.)
# ---------------------------------------------------------------------------
SIMPLE_PERSONALITIES: list[Personality] = [
    Personality("basic", "peacefully-expanding",   BASE_DEV_COST, BASE_CONQUER_COST),
    Personality("basic", "aggressively-expanding", BASE_DEV_COST, BASE_CONQUER_COST),
    Personality("basic", "developing",             BASE_DEV_COST, BASE_CONQUER_COST),
]
