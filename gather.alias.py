embed
<drac2>

# Initial Avrae implementation of Kibble's Crafting v1.07 Gathering Tables
# NOTE: This does not do stat checks or use tool proficiencies, it is currently only doing the gathering table lookup
#
# Arguments can be passed in any order, and defaults are biome: forest, count: 1, type: reagents
#
# Usage:
#   !gather                           # Gather reagents 1 time from the forest
#
#   !gather game                      # Hunt for game 1 time in the forest
#   !gather materials                 # Gather materials 1 time in the forest
#   !gather reagents                  # Gather reagents 1 time in the forest
#
#   !gather -rr 2                     # Gather reagents 2 times from the forest
#   !gather desert                    # Gather reagents 1 time from the desert
#   !gather 'Outer Plane' -rr 20      # Gather reagents 20 times from the outer plane
#   !gather -rr 5 underground game    # Hunt game 5 times in the underground (different argument order)

# Constants 
d1, d2, d4, d6, d8, d10, d12 = "1", "1d2", "1d4", "1d6", "1d8", "1d10", "1d12"
COLOR, TABLE, DC = "color", "table", "dc"
DICE_INDEX, RARITY_INDEX, VARIETY_INDEX = 2, 3, 4

# Gathering Types
REAGENTS, MATERIALS, GAME = "reagents", "materials", "game"

# Reagents
COMMON, UNCOMMON, RARE, QUALITY = "common", "uncommon", "rare", "quality"
CURATIVE, POISONOUS, REACTIVE = "curative reagent", "poisonous reagent", "reactive reagent"
PRIMAL, ARCANE, DIVINE = "primal essence", "arcane essence", "divine essence"

# Materials
RUSTY_FANCY, SHORT, MEDIUM, LARGE = "slightly rusty fancy", "short", "medium", "large"
ARMOR, SCALES, ADAMANT, CARPACE, MITHRIL, PARTS, FLETCHING, BRANCHES = "discarded armor padding", "scale", "adamant", "carapace", "mithril", "part", "fletching", "branches"
SUPPLIES, WOOD, SCRAPS, FIREWOOD, ICE_STEEL, BRANCH, HAFT, ORE = "supplies", "wood", "scraps", "firewood", "ice steel", "branch", "short haft", "ore"

# Game
FRESH, INGREDIENTS, HIDE, WATER = "fresh", "ingredients", "hide", "water"

BIOME_METADATA_TABLE = {
             'forest': {COLOR: "#228B22", DC: 10},
             'desert': {COLOR: "#FAD5A5", DC: 10},
         'grasslands': {COLOR: "#77bf80", DC: 10},
              'marsh': {COLOR: "#36594c", DC: 10},
          'mountains': {COLOR: "#888888", DC: 10},
              'caves': {COLOR: "#272727", DC: 12},
        'underground': {COLOR: "#DDDDDD", DC: 12},
            'jungles': {COLOR: "#2AAA8A", DC: 12},
              'shore': {COLOR: "#4f42b5", DC: 12},
             'tundra': {COLOR: "#B4A995", DC: 12},
           'feylands': {COLOR: "#db8b97", DC: 14},
        'shadowlands': {COLOR: "#3b3b3b", DC: 14},
    'elemental plane': {COLOR: "<color>", DC: 14},
        'lower plane': {COLOR: "<color>", DC: 14},
        'upper plane': {COLOR: "<color>", DC: 14},
        'outer plane': {COLOR: "<color>", DC: 14}}

# Game Table
GAME_TABLE = {
         'forest': [[1, 30, d1, FRESH, INGREDIENTS],    [31, 60, d4, FRESH, INGREDIENTS],
                    [61, 90, d4, FRESH, INGREDIENTS],   [61, 90, d1, HIDE],
                    [90, 100, d8, FRESH, INGREDIENTS],  [90, 100, d4, HIDE]],
         'desert': [[31, 60, d1, FRESH, INGREDIENTS],   [61, 90, d1, SUPPLIES],
                    [91, 100, d6, FRESH, INGREDIENTS],  [91, 100, d1, LARGE, CARPACE]],
     'grasslands': [[1, 30, d1, FRESH, INGREDIENTS],    [31, 60, d4, FRESH, INGREDIENTS],
                    [61, 90, d4, FRESH, INGREDIENTS],   [61, 90, d1, HIDE],
                    [90, 100, d8, FRESH, INGREDIENTS],  [90, 100, d4, HIDE]],
          'marsh': [[31, 60, d1, SUPPLIES],             [61, 90, d4, FRESH, INGREDIENTS],
                    [91, 100, d4, FRESH, INGREDIENTS]],
      'mountains': [[31, 60, d1, SUPPLIES],             [61, 90, d4, SUPPLIES],
                    [91, 100, d6, FRESH, INGREDIENTS],  [91, 100, d1, LARGE, CARPACE]],
          'caves': [[1, 30, d1, FRESH, INGREDIENTS],    [31, 60, d4, FRESH, INGREDIENTS],
                    [61, 90, d4, HIDE],                 [91, 100, d6, FRESH, INGREDIENTS],
                    [91, 100, d4, HIDE]],
    'underground': [[1, 30, d1, SUPPLIES],              [31, 60, d1, FRESH, INGREDIENTS],
                    [61, 90, d1, HIDE],                 [91, 100, d6, FRESH, INGREDIENTS],
                    [91, 100, d4, HIDE]],
        'jungles': [[1, 30, d1, FRESH, INGREDIENTS],    [31, 60, d4, FRESH, INGREDIENTS],
                    [61, 90, d1, SUPPLIES],             [61, 90, d1, FRESH, WATER],
                    [91, 100, d4, FRESH, INGREDIENTS],  [91, 100, d1, RARE, SUPPLIES]],
          'shore': [[1, 30, d1, FRESH, INGREDIENTS],    [31, 60, d4, FRESH, INGREDIENTS],
                    [61, 90, d8, FRESH, INGREDIENTS],   [61, 90, d1, SUPPLIES],
                    [91, 100, d6, FRESH, INGREDIENTS],  [91, 100, d1, MEDIUM, CARPACE]],
         'tundra': [[31, 60, d1, FRESH, INGREDIENTS],   [61, 90, d4, FRESH, INGREDIENTS],
                    [61, 90, d1, HIDE],                 [91, 100, d6, FRESH, INGREDIENTS],     
                    [91, 100, d4, HIDE]]
}

# Materials Table
MATERIALS_TABLE = {
         'forest': [[1, 20, d4, FIREWOOD],              [21, 40, d12, COMMON, BRANCH], 
                    [41, 60, d4, QUALITY, BRANCH],      [61, 80, d1, UNCOMMON, BRANCH], 
                    [81, 95, d2, UNCOMMON, BRANCH],     [96, 100, d1, COMMON, PRIMAL]],
         'desert': [[21, 40, d12, SCALES],              [41, 60, d4, MEDIUM, CARPACE], 
                    [61, 80, d1, LARGE, CARPACE],       [90, 95, d2, RARE, SUPPLIES], 
                    [96, 100, d1, COMMON, ARCANE]],
     'grasslands': [[1, 20, d4, FIREWOOD],              [21, 40, d12, WOOD, SCRAPS],
                    [41, 60, d1, UNCOMMON, SUPPLIES],   [61, 80, d1, LARGE, SCRAPS],
                    [81, 95, d1, RARE, SUPPLIES],       [96, 100, d1, LARGE, SCRAPS]],
          'marsh': [[1, 20, d4, FIREWOOD],              [21, 40, d12, WOOD, SCRAPS],
                    [41, 60, d4, QUALITY, BRANCHES],    [61, 80, d1, SUPPLIES],
                    [81, 95, d1, UNCOMMON, BRANCH],     [96, 100, d1, COMMON, PRIMAL]],
      'mountains': [[1, 20, d4, FIREWOOD],              [21, 40, d12, FLETCHING],
                    [41, 60, d4, ADAMANT, ORE],         [61, 80, d1, MITHRIL, ORE],
                    [81, 95, d1, UNCOMMON, BRANCH],     [96, 100, d1, COMMON, PRIMAL]],
          'caves': [[11, 20, d1, ARMOR],                [21, 40, d12, SCALES],
                    [41, 60, d1, ADAMANT, ORE],         [61, 80, d1, LARGE, CARPACE],
                    [81, 95, d4, MITHRIL, ORE],         [96, 100, d1, COMMON, PRIMAL]],
    'underground': [[11, 20, d1, PARTS],                [21, 40, d4, SUPPLIES],
                    [41, 60, d1, MITHRIL, ORE],         [61, 80, d1, UNCOMMON, BRANCH],
                    [81, 95, d4, LARGE, CARPACE],       [96, 100, d1, COMMON, ARCANE]],
        'jungles': [[1, 10, d4, FIREWOOD],              [11, 20, d4, COMMON, BRANCHES],    
                    [21, 40, d4, SUPPLIES],             [41, 60, d1, UNCOMMON, SUPPLIES],   
                    [61, 95, d4, UNCOMMON, BRANCH],     [96, 100, d1, COMMON, PRIMAL]],
          'shore': [[11, 20, d1, SHORT, HAFT],          [21, 40, d1, MEDIUM, CARPACE],
                    [41, 60, d1, RARE, SUPPLIES],       [61, 80, d4, COMMON, BRANCH],
                    [81, 95, d1, RUSTY_FANCY, PARTS],   [96, 100, d1, COMMON, PRIMAL]],
         'tundra': [[11, 20, d1, WOOD, SCRAPS],         [21, 40, d1, FIREWOOD],
                    [41, 60, d1, SUPPLIES],             [61, 80, d1, UNCOMMON, SUPPLIES],
                    [81, 95, d4, ICE_STEEL, ORE],       [96, 100, d1, COMMON, PRIMAL]]
}

# Reagents Table
REAGENT_TABLE = {
         'forest': [[11, 40, d1, COMMON, CURATIVE],     [41, 50, d1, COMMON, POISONOUS],     
                    [51, 60, d1, COMMON, REACTIVE],     [61, 70, d4, COMMON, POISONOUS], 
                    [71, 80, d4, COMMON, CURATIVE],     [81, 90, d1, UNCOMMON, CURATIVE],     
                    [91, 95, d1, UNCOMMON, POISONOUS],  [96, 100, d1, UNCOMMON, PRIMAL]],
         'desert': [[21, 40, d1, COMMON, REACTIVE],     [41, 50, d1, COMMON, CURATIVE],     
                    [51, 60, d1, COMMON, POISONOUS],    [61, 70, d2, COMMON, REACTIVE], 
                    [71, 80, d2, COMMON, REACTIVE],     [81, 90, d1, UNCOMMON, REACTIVE],     
                    [91, 95, d1, UNCOMMON, POISONOUS],  [96, 100, d1, COMMON, ARCANE]],
     'grasslands': [[21, 40, d1, COMMON, CURATIVE],     [41, 50, d1, COMMON, REACTIVE],     
                    [51, 60, d1, COMMON, POISONOUS],    [61, 70, d2, COMMON, POISONOUS], 
                    [71, 80, d2, COMMON, REACTIVE],     [81, 90, d1, UNCOMMON, REACTIVE],     
                    [91, 95, d1, UNCOMMON, POISONOUS],  [96, 100, d1, COMMON, ARCANE]],
          'marsh': [[11, 40, d1, COMMON, POISONOUS],    [41, 50, d1, COMMON, CURATIVE],     
                    [51, 60, d1, COMMON, REACTIVE],     [61, 70, d4, COMMON, POISONOUS], 
                    [71, 80, d4, COMMON, REACTIVE],     [81, 90, d1, UNCOMMON, POISONOUS],     
                    [91, 95, d1, UNCOMMON, REACTIVE],   [96, 100, d1, COMMON, PRIMAL]],
      'mountains': [[21, 40, d1, COMMON, REACTIVE],     [41, 50, d1, COMMON, CURATIVE],     
                    [51, 60, d1, COMMON, POISONOUS],    [61, 70, d2, COMMON, CURATIVE],
                    [71, 80, d2, COMMON, REACTIVE],     [81, 90, d1, UNCOMMON, REACTIVE],     
                    [91, 95, d1, COMMON, CURATIVE],     [96, 100, d1, COMMON, PRIMAL]],
          'caves': [[11, 30, d1, COMMON, REACTIVE],     [31, 50, d1, COMMON, POISONOUS],     
                    [51, 60, d4, COMMON, REACTIVE],     [61, 70, d1, UNCOMMON, REACTIVE],
                    [71, 80, d1, UNCOMMON, CURATIVE],   [81, 90, d1, COMMON, DIVINE],         
                    [91, 95, d1, UNCOMMON, POISONOUS],  [96, 100, d1, UNCOMMON, DIVINE]],
    'underground': [[11, 30, d1, COMMON, POISONOUS],    [31, 50, d1, COMMON, REACTIVE],     
                    [51, 60, d4, COMMON, POISONOUS],    [61, 70, d1, UNCOMMON, POISONOUS],
                    [71, 80, d1, UNCOMMON, CURATIVE],   [81, 90, d1, COMMON, DIVINE],         
                    [91, 95, d1, UNCOMMON, POISONOUS],  [96, 100, d1, UNCOMMON, DIVINE]],
        'jungles': [[11, 30, d1, COMMON, CURATIVE],     [31, 50, d1, COMMON, POISONOUS],     
                    [51, 60, d4, COMMON, CURATIVE],     [61, 70, d1, UNCOMMON, CURATIVE],
                    [71, 80, d1, UNCOMMON, REACTIVE],   [81, 90, d1, COMMON, PRIMAL],         
                    [91, 95, d1, UNCOMMON, REACTIVE],   [96, 100, d1, UNCOMMON, PRIMAL]],
          'shore': [[11, 30, d1, COMMON, CURATIVE],     [31, 50, d1, COMMON, POISONOUS],     
                    [51, 60, d4, COMMON, CURATIVE],     [61, 70, d1, UNCOMMON, REACTIVE],
                    [71, 80, d1, UNCOMMON, REACTIVE],   [81, 90, d1, COMMON, PRIMAL],         
                    [91, 95, d1, UNCOMMON, REACTIVE],   [96, 100, d1, UNCOMMON, PRIMAL]],
         'tundra': [[11, 30, d1, COMMON, REACTIVE],     [31, 50, d1, COMMON, CURATIVE],     
                    [51, 60, d4, COMMON, REACTIVE],     [61, 70, d1, UNCOMMON, CURATIVE],
                    [71, 80, d1, UNCOMMON, REACTIVE],   [81, 90, d1, COMMON, PRIMAL],         
                    [91, 95, d1, UNCOMMON, REACTIVE],   [96, 100, d1, UNCOMMON, PRIMAL]],
       'feylands': [[1, 20, d1, COMMON, CURATIVE],      [21, 40, d1, COMMON, REACTIVE],     
                    [41, 60, d4, COMMON, REACTIVE],     [61, 80, d1, UNCOMMON, CURATIVE],     
                    [81, 99, d1, UNCOMMON, PRIMAL],     [100, 100, d1, RARE, PRIMAL]],
    'shadowlands': [[1, 20, d1, COMMON, POISONOUS],     [21, 40, d1, COMMON, REACTIVE],     
                    [41, 60, d4, COMMON, POISONOUS],    [61, 80, d1, UNCOMMON, POISONOUS], 
                    [81, 99, d1, UNCOMMON, ARCANE],     [100, 100, d1, RARE, ARCANE]],
'elemental plane': [[1, 20, d1, COMMON, REACTIVE],      [21, 40, d1, COMMON, CURATIVE],     
                    [41, 60, d4, COMMON, REACTIVE],     [61, 80, d1, UNCOMMON, REACTIVE], 
                    [81, 99, d1, UNCOMMON, PRIMAL],     [100, 100, d1, RARE, PRIMAL]],
    'lower plane': [[1, 20, d1, COMMON, POISONOUS],     [21, 40, d1, COMMON, REACTIVE],     
                    [41, 60, d4, COMMON, POISONOUS],    [61, 80, d1, UNCOMMON, REACTIVE],     
                    [81, 99, d1, UNCOMMON, ARCANE],     [100, 100, d1, RARE, ARCANE]],
    'upper plane': [[1, 20, d1, COMMON, CURATIVE],      [21, 40, d1, COMMON, REACTIVE],     
                    [41, 60, d4, COMMON, CURATIVE],     [61, 80, d1, UNCOMMON, CURATIVE],     
                    [81, 99, d1, UNCOMMON, DIVINE],     [100, 100, d1, UNCOMMON, DIVINE]],
    'outer plane': [[1, 20, d1, COMMON, REACTIVE],      [21, 40, d1, COMMON, REACTIVE],     
                    [41, 60, d4, COMMON, REACTIVE],     [61, 80, d1, UNCOMMON, REACTIVE],     
                    [81, 99, d1, UNCOMMON, ARCANE],     [100, 100, d4, RARE, ARCANE]]
}

# Maps
TABLE_MAP = {
    REAGENTS: REAGENT_TABLE,
    MATERIALS: MATERIALS_TABLE,
    GAME: GAME_TABLE
}

VERB_MAP = {
    REAGENTS: "gathering reagents",
    MATERIALS: "gathering materials",
    GAME: "hunting game"
}

# Arguments
def parse_biome(gather_table, args):
    for biome in biome_names(gather_table):
        if biome in args:
            return biome
    return "forest"

def parse_skill(args):
    the_string = []
    ch = character()

    for name,skill in ch.skills:
        for arg in args:
            if arg.lower().replace(' ','') == name.lower():
                return arg.lower().capitalize()
    
    return None
    
def parse_count(args):
    a = argparse(&ARGS&)
    bonus = (''.join(a.get('rr', type_=lambda x: "+"+x if x[0] not in "+-" else x)))
    return 1 if bonus == "" else int(bonus)

def parse_type(args):
    for arg in [REAGENTS, MATERIALS, GAME]:
        if arg in args:
            return arg
    return REAGENTS

def parse_args(args):
    count = parse_count(args)
    if count > 100 or count < 1:
        err(f"Cannot gather more than 100 times, try a smaller number.")

    type = parse_type(args)
    gather_table = gather_table_for_type(type)
    biome = parse_biome(gather_table, args)
    skill = parse_skill(args)

    return biome, count, type, skill, gather_table

# Utility
def gather_table_for_type(type):
    return TABLE_MAP.get(type, REAGENT_TABLE)
    
def biome_table_lookup(gather_table, name):
    return gather_table.get(name, {})

def range_lookup(table, roll):
    matches = [row for row in table if row[0] <= roll <= row[1]]
    return matches if matches else [None]

def color_lookup(name):
    if name not in BIOME_METADATA_TABLE:
        err(f"Looking for color of unknown biome '{name}'.")
    return BIOME_METADATA_TABLE[name][COLOR]

def biome_names(gather_table):
    return list(gather_table.keys())

def verb_for_type(type):
    return VERB_MAP.get(type)

def lookup_result(table):
    dice = table[DICE_INDEX]

    rarity = table[RARITY_INDEX]
    variety = None

    if len(table) > VARIETY_INDEX:
        variety = table[VARIETY_INDEX]

    count = vroll(dice).total
    if variety == None:
        return [rarity] * count
    
    return [rarity + " " + variety] * count

def roll_lookup(gather_table, name, roll):
    found_biome_table = biome_table_lookup(gather_table, name)
    if found_biome_table == None:
        err(f"Could not find biome named '{name}'. Please choose from {', '.join(biome_names(gather_table))}.")
    
    table_list = range_lookup(found_biome_table, roll)
    results = []
    for table in table_list:
        if table == None:
            results.append(["nothing"])
        else:
            results.append(lookup_result(table))
    return results

def remove_items(test_list, item):
    return [i for i in test_list if i != item] 

def foraged_display_name(foraged, count):
    name = (f"{count}x" if count > 0 else f"No ") + f" {foraged}"
    if BRANCH in name and count != 1:
        name = name + "e"
    return name + ("s" if count != 1 and name[-1] != "s" else "")

def count_of(items, item):
    return items.count(item)

# Core Logic
def simulate_foraging(gather_table, forage_count):
    all_rolls = []
    all_foraged = []
    for i in range(forage_count):
        forage_roll = vroll("1d100").total
        foraged_array = roll_lookup(gather_table, biome, forage_roll)
        all_rolls.append(str(forage_roll))
        for foraged in foraged_array:
            all_foraged.extend(foraged)
    
    return all_rolls, all_foraged 

def count_foraged(all_foraged):
    counted_all_foraged = []

    while len(all_foraged) > 0:
        foraged = all_foraged.pop()
        if foraged == "nothing":
            continue
        count_foraged = count_of(all_foraged, foraged) + 1
        all_foraged = remove_items(all_foraged, foraged)
        display_name = foraged_display_name(foraged, count_foraged)
        counted_all_foraged.append(display_name)
    
    return counted_all_foraged

def card_values(gather_table, verb, biome, rolls, found, skill):
    dice_strings = len(rolls) + "d100 = `(" + ', '.join(rolls) + ")`"
    color = color_lookup(biome)
    title = f"{character().name} is {verb} in the {biome}"
    if skill:
        title += f" with their {skill} skill."
    else:
        title += "."

    if len(found) > 1:
        description = f"They found:\n"
        for foraged in found:
            description += "  • " + foraged + "\n"
    else:
        description = f"They found {found[0]}!" if found else "They found nothing!"

    footer = f"{dice_strings}"
    return title, description, footer, color

biome, attempt_count, type, skill, gather_table = parse_args(&ARGS&)
verb = verb_for_type(type)

forage_rolls, forage_results = simulate_foraging(gather_table, attempt_count)
counted_results = count_foraged(forage_results)
title, description, footer, color = card_values(gather_table, verb, biome, forage_rolls, counted_results, skill)


</drac2>

-title "{{title}}"
-desc "{{description}}"
-f "{{footer}}"
-color "{{color}}"
-thumb "<image>"
