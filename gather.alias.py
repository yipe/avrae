embed
<drac2>

# Initial Avrae implementation of Kibble's Crafting v1.07 Gathering
# NOTE: This script currently only supports forest and desert biome gathering of reagents.
# NOTE: This does not do stat checks or use tool proficiencies, it is currently only the gathering table lookup

# Usage:
#   !gather             # Gather 1 time from the forest (default)
#   !gather desert      # Gather 1 time from the desert
#   !gather forest 20   # Gather 20 times from the forest

# Constants 
DICE = ["1", "1d2", "1d4", "1d6", "1d8", "1d8", "1d12"] 
RARITIES = ["common", "uncommon"] 
VARITIES = ["curative", "poisonous", "reactive", "primal", "arcane"]
MATERIALS = ["reagent", "essence"] 
DICE_INDEX, RARITY_INDEX, VARIETY_INDEX, MATERIAL_INDEX = 2, 3, 4, 5 # Indices
BIOMES = ["forest", "desert", "grasslands", "marsh", "mountains", "caves", "underground", "jungles", "shore", "tundra", "feylands", "shadowlands", "elemental plane", "lower plane", "upper plane", "outer plane"] 
BIOME_COLORS = ["#228B22", "#FAD5A5", "#77bf80",  "#36594c", "#888888", "#272727", "#DDDDDD", "#2AAA8A", "#4f42b5", "#B4A995", "#db8b97", "<color>", "<color>", "<color>", "<color>", "<color>"]
REAGENTS =  [
		[ # forest
			[11, 20, 0, 0, 0, 0], [21, 40, 0, 0, 0, 0], [41, 50, 0, 0, 1, 0],
			[51, 60, 0, 0, 2, 0], [61, 70, 2, 0, 1, 0], [71, 80, 2, 0, 0, 0],
			[81, 90, 0, 1, 0, 0], [91, 95, 0, 1, 1, 0], [96, 100, 0, 1, 3, 1]],
		[ # desert
			[21, 40, 0, 0, 2, 0], [41, 50, 0, 0, 0, 0], [51, 60, 0, 0, 1, 0],
			[61, 70, 1, 0, 2, 0], [71, 80, 1, 0, 2, 0], [81, 90, 0, 1, 2, 0],
			[91, 95, 0, 1, 1, 0], [96, 100, 0, 0, 4, 1]]
	]

# Prune biome list until we support them all
BIOMES = BIOMES[0:len(REAGENTS)]

# Arguments
def parse_args(args):
    biome = BIOMES[0]
    count = 1

    arg_count = len(args)
    if arg_count > 0:
        biome = args[0]
        
    if arg_count > 1:
        if args[1].isnumeric():
            count = int(args[1])
            if count < 1 or count > 100:
                err(f"Second argument must be a number between 1 and 100.")
        else:
            err(f"Second argument must be a number between 1 and 100.")
            
    if count > 100:
        err(f"Could not forage more than 100 times, try a smaller number.")

    return biome, count

# Utility
def biome_lookup(name):
	if name not in BIOMES:
		return None
	ti = BIOMES.index(name)
	return REAGENTS[ti]	

def range_lookup(table, roll):
	for row in table:
		if row[0] <= roll <= row[1]: 
			return row
	return None

def color_from_name(name):
	biome_index = BIOMES.index(name)
	return BIOME_COLORS[biome_index]

def roll_lookup(name, roll):
	table = biome_lookup(name)
	if table == None:
			err(f"Could not find biome named '{name}'. Please choose from {', '.join(BIOMES)}.")
	
	t = range_lookup(table, roll)
	if t == None:
		return ["nothing"]
	d, r, v, m = DICE[t[DICE_INDEX]], RARITIES[t[RARITY_INDEX]], VARITIES[t[VARIETY_INDEX]], MATERIALS[t[MATERIAL_INDEX]]
	c = vroll(d).total
	fname = r + " " + v + " " + m
	return [fname] * c

def remove_items(test_list, item):
	res = [i for i in test_list if i != item] 
	return res 

def foraged_display_name(foraged, count):
	if count == 0:
		return "NONE LOL"
	if count == 1:
		return "1x " + foraged
	return str(count) + "x " + foraged + "s"

def count_of(items, item):
	c = 0
	for this_item in items:
		if item == this_item:
			c = c + 1
	return c

# Core Logic
def simulate_foraging(forage_count):
    all_rolls = []
    all_foraged = []
    for i in range(forage_count):
    	forage_roll = vroll("1d100").total
    	foraged = roll_lookup(biome, forage_roll)
    	all_rolls.append(str(forage_roll))
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

def card_values(biome, rolls, found):
    dice_strings = len(rolls) + "d100 = `(" + ', '.join(rolls) + ")`"
    color = color_from_name(biome)
    title = f"{character().name} is gathering reagents in the {biome}"
    description = f"They found nothing!"
    if len(found) == 1:
        description = f"They found {found[0]}!"
    elif len(found) > 1:
        description = f"They found:\n"
        for foraged in found:
            description += "  • " + foraged + "\n"

    footer = f"{dice_strings}"
    return title, description, footer, color

biome, attempt_count = parse_args(&ARGS&)
forage_rolls, forage_results = simulate_foraging(attempt_count)
counted_results = count_foraged(forage_results)
title, description, footer, color = card_values(biome, forage_rolls, counted_results)

</drac2>

-title "{{title}}"
-desc "{{description}}"
-f "{{footer}}"
-color "{{color}}"
-thumb "<image>"
