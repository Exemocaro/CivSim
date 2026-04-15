"""Procedural fantasy name generator for characters."""

from __future__ import annotations

import random

_PREFIXES = [
    "Aex",
    "Aem",
    "Aux",
    "Adr",
    "Ador",
    "Adox",
    "Aft",
    "Al",
    "Ax",
    "Arl",
    "Arn",
    "Arg",
    "Alfr",
    "Am",
    "An",
    "Bae",
    "Bal",
    "Ber",
    "Bex",
    "Bru",
    "Brian",
    "Bro",
    "Caet",
    "Car",
    "Cal",
    "Caerl",
    "Caex",
    "Con",
    "Caun",
    "Daec",
    "Daex",
    "Daux",
    "Deir",
    "Dev",
    "Derv",
    "Daerv",
    "Don",
    "Eag",
    "Eax",
    "Ean",
    "Eit",
    "Ein",
    "Et",
    "Ev",
    "Eun",
    "Eux",
    "Earx",
    "Faol",
    "Fael",
    "Faex",
    "Faeg",
    "Faen",
    "Ferg",
    "Fan",
    "Fin",
    "Gal",
    "Gaux",
    "Gaex",
    "Ger",
    "Gael",
    "Gon",
    "Grat",
    "Glan",
    "Ian",
    "Iu",
    "Itad",
    "Ix",
    "Jaex",
    "Jar",
    "Jon",
    "Jair",
    "Jan",
    "Jen",
    "Jap",
    "Jor",
    "Joer",
    "Jord",
    "Lad",
    "Laex",
    "Lor",
    "Loex",
    "Loer",
    "Lais",
    "Lon",
    "Loen",
    "Liv",
    "Laen",
    "Mar",
    "Mag",
    "Maer",
    "Maex",
    "Max",
    "Maur",
    "Mor",
    "Moert",
    "Moerx",
    "Mic",
    "Mial",
    "Mel",
    "Mil",
    "Mual",
    "Muax",
    "Mur",
    "Nar",
    "Nat",
    "Nal",
    "Nan",
    "Naen",
    "Naex",
    "Nael",
    "Nair",
    "Nil",
    "Niun",
    "Non",
    "Nor",
    "Nur",
    "Nourb",
    "Nour",
    "Nob",
    "Pan",
    "Paen",
    "Paex",
    "Pax",
    "Pair",
    "Paix",
    "Por",
    "Pur",
    "Pab",
    "Prud",
    "Praed",
    "Praid",
    "Rad",
    "Raed",
    "Rar",
    "Ren",
    "Rian",
    "Ron",
    "Rob",
    "Roan",
    "Ruan",
    "Ruen",
    "Sal",
    "San",
    "Sar",
    "Saex",
    "Saep",
    "Saeb",
    "Sen",
    "Seb",
    "Serm",
    "Sior",
    "Sim",
    "Sin",
    "Siun",
    "Soun",
    "Son",
    "Sob",
    "Sor",
    "Sran",
    "Sren",
    "Tan",
    "Tain",
    "Train",
    "Taex",
    "Taen",
    "Taer",
    "Ter",
    "Trist",
    "Trun",
    "Tun",
    "Tub",
    "Ur",
    "Uar",
    "Uir",
    "Uan",
    "Uen",
    "Uex",
    "Uix",
    "Ust",
    "Ulr",
    "Ualt",
    "Uarn",
    "Uam",
    "Val",
    "Vaex",  # fixed: was missing comma causing "VaexVaen" concatenation
    "Vaen",
    "Vaeb",
    "Vob",
    "Vor",
    "Vorn",
    "Vourn",
    "Vur",
    "Vurn",
    "Viv",
    "Viol",
    "Vion",
    "Vict",
    "Vic",
    "Vix",
    "Vaer",
    "Vaern",
    "Vov",
    "Vuv",
    "Vuav",
    "Vuiv",
    "Vuin",
    "Vuan",
    "Vuen",
    "Vun",
    "Xav",
    "Xaev",
    "Xaen",
    "Xan",
    "Xen",
    "Xin",
    "Xov",
    "Xuv",
    "Xuiv",
]

_STEMS = [
    "",
    "and",
    "an",
    "ab",
    "ad",
    "at",
    "ac",
    "ar",
    "ant",
    "en",
    "end",
    "er",
    "ent",
    "ic",
    "in",
    "ind",
    "ir",
    "int",
    "on",
    "ond",
    "or",
    "oi",
    "un",
    "und",
    "ur",
    "urs",
]

_MALE_SUFFIXES = [
    "aex",
    "ae",
    "ar",
    "ax",
    "ael",
    "aen",
    "as",
    "air",
    "eux",
    "eus",
    "ir",
    "id",
    "ior",
    "iel",
    "or",
    "os",
    "on",
    "ur",
    "uan",
    "uir",
    "un",
    "us",
]

_FEMALE_SUFFIXES = [
    "ae",
    "a",
    "aia",
    "e",
    "eia",
    "i",
    "ia",
    "is",
    "ix",
    "ias",
]


def name_gen(gender: str = "") -> str:
    """Return a randomly generated fantasy name.

    Args:
        gender: ``"m"`` for male, ``"f"`` for female, or ``""`` to pick at random.

    Returns:
        A capitalised fantasy name string.
    """
    if gender == "":
        gender = random.choice(["m", "f"])

    pre = random.choice(_PREFIXES)
    name = pre

    # Longer prefixes rarely get a stem; shorter ones do more often
    r = random.randint(1, 10)
    needs_stem = (len(pre) >= 4 and r == 10) or (len(pre) < 4 and r >= 8)

    if needs_stem:
        stem = random.choice(_STEMS)
        # Avoid stems that make an awkward name when the prefix has no 't' or 'x'
        attempts = 0
        while (
            "t" not in pre
            and "t" not in stem
            and "x" not in pre
            and "x" not in stem
            and not pre.startswith("x")
            and attempts < 20
        ):
            stem = random.choice(_STEMS)
            attempts += 1
        name += stem

    if gender == "m":
        name += random.choice(_MALE_SUFFIXES)
    elif gender == "f":
        name += random.choice(_FEMALE_SUFFIXES)
    else:
        return "Unknown"

    return name[0].upper() + name[1:]


def generate_names(num: int) -> None:
    """Print *num* example male/female name pairs — useful for testing."""
    for _ in range(num):
        print(f"Male:   {name_gen('m')}")
        print(f"Female: {name_gen('f')}")
