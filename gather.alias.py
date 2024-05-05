embed
<drac2>

# Initial Avrae implementation of Kibble's Crafting v1.07 Gathering Tables
# This will do the appropraite skill checks and lookups based on the number of successful checks
#
# Arguments can be passed in any order.
#
# Usage examples:
# 
#   !gather                           # Attempt to gather one reagent from the forest
#
# You can specify the gathering (defaults to reagents)
#
#   !gather game                      # Hunt for game
#   !gather materials                 # Gather materials
#   !gather reagents                  # Gather reagents
#
# You can specify the number of times to gather (defaults to 1)
# 
#   !gather -rr 2                     # Gather reagents 2 times from the forest (max 50)
#
# You can specify the biome (detaults to forest):
#
#   !gather desert                    # Gather reagents 1 time from the desert
#   !gather 'Outer Plane' -rr 20      # Gather reagents 20 times from the outer plane
#
# You can specify proficiency or expertise for the check
#   !gather exp                       # Gather reagents with expertise
#   !gather pro                       # Gather reagents with proficiency
# 
# You can specify the standard mofifiers for the check:
#   !gather -b +2                     # Gather reagents with a +2 bonus
#   !gather adv                       # Gather reagents with advantage (or disadvantage)
#   !gather guidance                  # Gather reagents with guidance
#
# You can optionally change the DC for the biome
#
#  !gather -dc 15                    # Gather reagents with a DC of 15, representing some added difficulty
#
# You can also combine them all together.
# This gathers materials in the caves 10 times with proficiency, advantage, guidance, +2 bonus, and a DC of 15
# 
#   !gather materials caves pro adv guidance -b 2 -rr 10 -dc 15
#
# Notes: 
# - This script will automatically use Herbalism Kit Proficiency & Expertise if the player is using Tool Check (https://avrae.io/dashboard/workshop/630b0e39b85ea38890666c08)
#   Passing in 'pro' or 'exp' will override any Tool Check Values present.
#
# - Checks will automatically use the highest ability score, no need to pass any in. 
#  [TODO] In the future this can be overriden. 
#
# - This will automatically use the appropriate skill for the check.
# - When performing skill checks, this automatically uses Jack of All Trades, Proficiency/Expertise, Halfling Luck, and Reliable Talent without needing to pass in any values.
#  [TODO] In the future this can be overriden. 

# Constants 
MAX_ATTEMPTS = 50 # More than this and it times out
d1, d2, d4, d6, d8, d10, d12 = "1", "1d2", "1d4", "1d6", "1d8", "1d10", "1d12"
COLOR, TABLE, DC = "color", "table", "dc"
DICE_INDEX, RARITY_INDEX, VARIETY_INDEX = 2, 3, 4

SURVIVAL, WISDOM, STRENGTH, DEXTERITY = "survival", "wisdom", "strength", "dexterity"
HERBALISM_KIT = "Herbalism Kit"

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
    REAGENTS: "gathering",
    MATERIALS: "gathering",
    GAME: "hunting"
}

# Arguments
def parse_biome(gather_table, args):
    for biome in biome_names(gather_table):
        if biome in args:
            return biome
    return "forest"

def parse_dc(args):
    a = argparse(args)
    bonus = ''.join(a.get('dc'))
    return int(bonus) if bonus else None

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

def parse_proficiency(args):
    expertise = "exp" in args
    proficiency = "pro" in args or "prof" in args
    return proficiency, expertise

def parse_args(args):
    count = parse_count(args)
    if count > MAX_ATTEMPTS or count < 1:
        err(f"Cannot gather more than {MAX_ATTEMPTS} times, try a smaller number.")

    type = parse_type(args)
    gather_table = gather_table_for_type(type)
    biome = parse_biome(gather_table, args)
    skill = parse_skill(args)
    dc = parse_dc(args)

    return args, biome, count, type, skill, dc, gather_table

# Utility
def gather_table_for_type(type):
    return TABLE_MAP.get(type, REAGENT_TABLE)
    
def biome_table_lookup(gather_table, name):
    return gather_table.get(name, {})

def range_lookup(table, roll):
    matches = [row for row in table if row[0] <= roll <= row[1]]
    return matches if matches else [None]

def color_for_biome_lookup(name):
    if name not in BIOME_METADATA_TABLE:
        err(f"Looking for color of unknown biome '{name}'.")
    return BIOME_METADATA_TABLE[name][COLOR]

def dc_for_biome_lookup(name):
    if name not in BIOME_METADATA_TABLE:
        err(f"Looking for DC of unknown biome '{name}'.")
    return BIOME_METADATA_TABLE[name][DC]

def biome_names(gather_table):
    return list(gather_table.keys())

def verb_for_type(type):
    return VERB_MAP.get(type)

def lookup_result(table):
    dice = table[DICE_INDEX]
    rarity = table[RARITY_INDEX]
    variety = table[VARIETY_INDEX] if len(table) > VARIETY_INDEX else None
    count = vroll(dice).total

    if variety == None:
        return [rarity] * count
    
    return [rarity + " " + variety] * count

def roll_lookup(gather_table, name, roll):
    found_biome_table = biome_table_lookup(gather_table, name)
    if found_biome_table == None:
        err(f"Could not find biome named '{name}'. Please choose from {', '.join(biome_names(gather_table))}.")
    
    table_list = range_lookup(found_biome_table, roll.total)
    return [lookup_result(table) if table else ["nothing"] for table in table_list]
    

def remove_items(test_list, item):
    return [i for i in test_list if i != item] 

def foraged_display_name(foraged, count):
    name = (f"{count}x" if count > 0 else f"No ") + f" {foraged}"
    if BRANCH in name and count != 1:
        name = name + "e"
    return name + ("s" if count != 1 and name[-1] != "s" else "")

def count_of(items, item):
    return items.count(item)

# Skill Checks
def roll_for_skill(args, skill, addedBonus = None):
    ch = character()
    a = argparse(args)

    # Parse for advantage
    adv = a.adv(boolwise=True)

    # Halfling Luck: Grab the reroll number if the character has the csetting reroll or default to None
    reroll_number = ch.csettings.get("reroll", None)

    # Grab a minimum from our args like a standard !check, (-mc #) or set it to 10 if the character has the csetting 'talent' set to True and has proficiency or expertise in the chosen skill.
    minimum_check = a.last('mc', None, int) or (10 if ch.csettings.get("talent", False) and ch.skills[skill].prof>=1 else None)
    
    # Add bonuses, if any and add them to our roll. 
    bonus = (''.join(a.get('b', type_=lambda x: "+"+x if x[0] not in "+-" else x))) + ('+1d4' if a.get('guidance') else '')

    if addedBonus:
        bonus = bonus + addedBonus

    return vroll(ch.skills[skill].d20(adv, reroll_number, minimum_check) + bonus)

def best_searching_stat():
    stats = {STRENGTH: strength, DEXTERITY: dexterity, WISDOM: wisdom}
    return max(stats, key=stats.get)

def best_hunting_stat():
    stats = {DEXTERITY: dexterity, WISDOM: wisdom}
    return max(stats, key=stats.get)
    
def herbalism_kit_proficiency_bonus(proficiency, expertise):
    if expertise:
        return "+" + 2 * proficiencyBonus

    if proficiency:
        return "+" + proficiencyBonus    
    
    # If neither 'pro' or 'exp' are in args, look for Tool Check values
    cvars = character().cvars
    if "eTools" in cvars and HERBALISM_KIT in cvars["eTools"]:
        return " +" + 2 * proficiencyBonus 
    
    if "pTools" in cvars and HERBALISM_KIT in cvars["pTools"]:
        return "+" + proficiencyBonus

    return None

def survival_proficiency_bonus():
    survival = character().skills[SURVIVAL]
    return "+ " + survival.prof * proficiencyBonus


def survival_modifier_bonus():
    survival = character().skills[SURVIVAL]
    if survival.prof >= 1:
        return "+ " + survival.value
    return None

def arg_parse_action_type(args):
    for action in ALLOWED_GATHER_COMMANDS:
        if action in args:
            return action
    return None

def skill_roll_for_action(args, action):
    proficiency, expertise = parse_proficiency(args)

    if action == REAGENTS:
        return roll_for_skill(args, WISDOM, herbalism_kit_proficiency_bonus(proficiency, expertise))
    
    if action == MATERIALS:
        return roll_for_skill(args, best_searching_stat(), survival_proficiency_bonus())
    
    if action == GAME:
        return roll_for_skill(args, best_hunting_stat(), survival_modifier_bonus())
    
    return None

# Core Logic
def simulate_foraging(gather_table):
    all_rolls = []
    all_foraged = []
    forage_roll = vroll("1d100")
    foraged_array = roll_lookup(gather_table, biome, forage_roll)
    for foraged in foraged_array:
        all_foraged.extend(foraged)
    
    return forage_roll, all_foraged 

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

def card_values(verb, type, biome, found, skill):
    
    color = color_for_biome_lookup(biome)
    title = f"{character().name} is {verb} {type} in the {biome}."

    if len(found) > 1:
        description = f"They found:\n"
        for foraged in found:
            description += "  • " + foraged + "\n"
    else:
        description = f"They found {found[0]}!" if found else "They found nothing!"

    
    return title, description, color

def strip_parens(dice_string):
    while True:
        start = dice_string.find("(")
        end = dice_string.find(")")
        if start == -1 or end == -1:
            return dice_string        
        new_dice_string = dice_string[:start] + dice_string[end+1:]
        if new_dice_string == dice_string:
            return dice_string
        dice_string = new_dice_string

def card_footer(skill_rolls, dc, verb):
    footer = f"**Check DC**: {dc}\n\n"
    if len(skill_rolls) == 1:
        skill_roll, forage_roll = skill_rolls[0]
        footer += f"**{verb.title()} Check**: {skill_roll}"
        if forage_roll:
            footer += f"; Success!\n**Lookup Check**: {forage_roll}\n"
        else:
            footer += f"; Failure!\n"
    else:
        dice_string = strip_parens(skill_rolls[0][0].dice)        

        skill_roll_values = [skill_roll.total for skill_roll, _ in skill_rolls]
        forage_roll_values = [forage_roll.total for _, forage_roll in skill_rolls if forage_roll]        
        dice_values = ', '.join([f"{value}" if value >= dc else f"~~{value}~~" for value in skill_roll_values])
        footer += f"**{verb.title()} Checks**: {len(skill_rolls)} x ({dice_string}) = ({dice_values})\n"
        if len(forage_roll_values) > 0:
            dice_values = ', '.join([str(value) for value in forage_roll_values])
            footer += f"**Lookup Checks**: {len(forage_roll_values)}d100 = ({dice_values})\n"

    return footer
    
def forage(gather_table, attempt_count, dc):
    forage_results = []
    skill_rolls = []
    for i in range(attempt_count): 
        skill_roll = skill_roll_for_action(args, type)
        success = skill_roll.total >= dc
        forage_roll = None
        if success:
            forage_roll, results = simulate_foraging(gather_table)
            forage_results.extend(results)
        skill_rolls.append([skill_roll, forage_roll])
    return skill_rolls, forage_results

# Core Logic

args, biome, attempt_count, type, skill, dc, gather_table = parse_args(&ARGS&)
verb = verb_for_type(type)
if not dc:
    dc = dc_for_biome_lookup(biome)
skill_rolls, forage_results = forage(gather_table, attempt_count, dc)
counted_results = count_foraged(forage_results)
title, description, color = card_values(verb, type, biome, counted_results, skill)
footer = card_footer(skill_rolls, dc, verb)

</drac2>

-title "{{title}}"
-desc "{{description}}"
-f "{{footer}}"
-color "{{color}}"
-thumb "<image>"
