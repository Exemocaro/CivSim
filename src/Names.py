
# random name generator I made

import random

prefixes = [
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
"Maer",
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
"Vaex"
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

stems = [
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

male_suffixes = [
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
female_suffixes = [
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

# returns a random name given a gender
def name_gen(gender = ""):
    if gender == "":
        gender = random.choice(["m", "f"])
    n = ""
    has_stem = False

    pre = random.choice(prefixes)
    n += pre
    r = random.randint(1, 10)

    if len(pre) >= 4:
        if r == 10:
            has_stem = True
    else:
        if r >= 8:
            has_stem = True

    if has_stem:
        stem = random.choice(stems)
        while ('t' not in pre and 't' not in stem) and ('x' not in pre and 'x' not in stem and pre[0] != 'x'):
            stem = random.choice(stems)
        n += stem

    if gender == "m":
        n += random.choice(male_suffixes)
    elif gender == "f":
        n += random.choice(female_suffixes)
    else:
        return "Error on gender"

    final_name = ""
    for c in n:
        if c == n[0]:
            final_name += n[0].upper()
        else:
            final_name += c

    return final_name

# generates 300 random names based on the function name_gen(), use this to test the names and see if you like them!
def generate_names(num):
    while num > 0:
        print(f"Male Name: {name_gen('m')}.")
        print(f"Female Name: {name_gen('f')}.")
        num -= 1


