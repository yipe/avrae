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
d1, d2, d4, d6, d8, d10, d12 = "1", "1d2", "1d4", "1d6", "1d8", "1d10", "1d12"
COMMON, UNCOMMON, RARE = "common", "uncommon", "rare"
CURATIVE, POISONOUS, REACTIVE = "curative reagent", "poisonous reagent", "reactive reagent"
PRIMAL, ARCANE, DIVINE = "primal essence", "arcane essence", "divine essence"

COLOR, TABLE, DC = "color", "table", "dc"
DICE_INDEX, RARITY_INDEX, VARIETY_INDEX = 2, 3, 4
REAGENTS =  {
	'forest': {COLOR: "#228B22", DC: 10, TABLE: 
		[[11, 40, d1, COMMON, CURATIVE], [41, 50, d1, COMMON, POISONOUS], [51, 60, d1, COMMON, REACTIVE], [61, 70, d4, COMMON, POISONOUS], 
		 [71, 80, d4, COMMON, CURATIVE], [81, 90, d1, UNCOMMON, CURATIVE], [91, 95, d1, UNCOMMON, POISONOUS], [96, 100, d1, UNCOMMON, PRIMAL]]},
	'desert': {COLOR: "#FAD5A5", DC: 10, TABLE:
		[[21, 40, d1, COMMON, REACTIVE], [41, 50, d1, COMMON, CURATIVE], [51, 60, d1, COMMON, POISONOUS],[61, 70, d2, COMMON, REACTIVE], 
		 [71, 80, d2, COMMON, REACTIVE], [81, 90, d1, UNCOMMON, REACTIVE], [91, 95, d1, UNCOMMON, POISONOUS], [96, 100, d1, COMMON, ARCANE]]},
	'grasslands': {COLOR: "#77bf80", DC: 10, TABLE:
		[[21, 40, d1, COMMON, CURATIVE], [41, 50, d1, COMMON, REACTIVE], [51, 60, d1, COMMON, POISONOUS], [61, 70, d2, COMMON, POISONOUS], 
		 [71, 80, d2, COMMON, REACTIVE], [81, 90, d1, UNCOMMON, REACTIVE], [91, 95, d1, UNCOMMON, POISONOUS], [96, 100, d1, COMMON, ARCANE]]},
	'marsh': {COLOR: "#36594c", DC: 10, TABLE:
		[[11, 40, d1, COMMON, POISONOUS], [41, 50, d1, COMMON, CURATIVE], [51, 60, d1, COMMON, REACTIVE], [61, 70, d4, COMMON, POISONOUS], 
		 [71, 80, d4, COMMON, REACTIVE], [81, 90, d1, UNCOMMON, POISONOUS], [91, 95, d1, UNCOMMON, REACTIVE], [96, 100, d1, COMMON, PRIMAL]]},
	'mountains': {COLOR: "#888888", DC: 10, TABLE: 
		[[21, 40, d1, COMMON, REACTIVE], [41, 50, d1, COMMON, CURATIVE], [51, 60, d1, COMMON, POISONOUS], [61, 70, d2, COMMON, CURATIVE],
		 [71, 80, d2, COMMON, REACTIVE], [81, 90, d1, UNCOMMON, REACTIVE], [91, 95, d1, COMMON, CURATIVE], [96, 100, d1, COMMON, PRIMAL]]},
	'caves': {COLOR: "#272727", DC: 12, TABLE: 
		[[11, 30, d1, COMMON, REACTIVE], [31, 50, d1, COMMON, POISONOUS], [51, 60, d4, COMMON, REACTIVE], [61, 70, d1, UNCOMMON, REACTIVE],
		 [71, 80, d1, UNCOMMON, CURATIVE], [81, 90, d1, COMMON, DIVINE], [91, 95, d1, UNCOMMON, POISONOUS], [96, 100, d1, UNCOMMON, DIVINE]]},
	'underground': {COLOR: "#DDDDDD", DC: 12,TABLE: 
		[[11, 30, d1, COMMON, POISONOUS], [31, 50, d1, COMMON, REACTIVE], [51, 60, d4, COMMON, POISONOUS], [61, 70, d1, UNCOMMON, POISONOUS],
		 [71, 80, d1, UNCOMMON, CURATIVE], [81, 90, d1, COMMON, DIVINE], [91, 95, d1, UNCOMMON, POISONOUS], [96, 100, d1, UNCOMMON, DIVINE]]},
	'jungles': {COLOR: "#2AAA8A", DC: 12, TABLE: 
		[[11, 30, d1, COMMON, CURATIVE], [31, 50, d1, COMMON, POISONOUS], [51, 60, d4, COMMON, CURATIVE], [61, 70, d1, UNCOMMON, CURATIVE],
		 [71, 80, d1, UNCOMMON, REACTIVE], [81, 90, d1, COMMON, PRIMAL], [91, 95, d1, UNCOMMON, REACTIVE], [96, 100, d1, UNCOMMON, PRIMAL]]},
	'shore': {COLOR: "#4f42b5", DC: 12, TABLE: 
		[[11, 30, d1, COMMON, CURATIVE], [31, 50, d1, COMMON, POISONOUS], [51, 60, d4, COMMON, CURATIVE], [61, 70, d1, UNCOMMON, REACTIVE],
		 [71, 80, d1, UNCOMMON, REACTIVE], [81, 90, d1, COMMON, PRIMAL], [91, 95, d1, UNCOMMON, REACTIVE], [96, 100, d1, UNCOMMON, PRIMAL]]},
	'tundra': {COLOR: "#B4A995", DC: 12, TABLE: 
		[[11, 30, d1, COMMON, REACTIVE], [31, 50, d1, COMMON, CURATIVE], [51, 60, d4, COMMON, REACTIVE], [61, 70, d1, UNCOMMON, CURATIVE],
		 [71, 80, d1, UNCOMMON, REACTIVE], [81, 90, d1, COMMON, PRIMAL], [91, 95, d1, UNCOMMON, REACTIVE], [96, 100, d1, UNCOMMON, PRIMAL]]},
	'feylands': {COLOR: "#db8b97", DC: 14, TABLE: 
		[[1, 20, d1, COMMON, CURATIVE], [21, 40, d1, COMMON, REACTIVE], [41, 60, d4, COMMON, REACTIVE], 
   		 [61, 80, d1, UNCOMMON, CURATIVE], [81, 99, d1, UNCOMMON, PRIMAL], [100, 100, d1, RARE, PRIMAL]]},
	'shadowlands': {COLOR: "<color>", DC: 14, TABLE: 
		[[1, 20, d1, COMMON, POISONOUS], [21, 40, d1, COMMON, REACTIVE], [41, 60, d4, COMMON, POISONOUS],
   		 [61, 80, d1, UNCOMMON, POISONOUS], [81, 99, d1, UNCOMMON, ARCANE], [100, 100, d1, RARE, ARCANE]]},
	'elemental plane': {COLOR: "<color>", DC: 14,  TABLE: 
		[[1, 20, d1, COMMON, REACTIVE], [21, 40, d1, COMMON, CURATIVE], [41, 60, d4, COMMON, REACTIVE],
   		 [61, 80, d1, UNCOMMON, REACTIVE], [81, 99, d1, UNCOMMON, PRIMAL], [100, 100, d1, RARE, PRIMAL]]},
	'lower plane': {COLOR: "<color>", DC: 14, TABLE: 
		[[1, 20, d1, COMMON, POISONOUS], [21, 40, d1, COMMON, REACTIVE], [41, 60, d4, COMMON, POISONOUS],
   		 [61, 80, d1, UNCOMMON, REACTIVE], [81, 99, d1, UNCOMMON, ARCANE], [100, 100, d1, RARE, ARCANE]]},
	'upper plane': {COLOR: "<color>", DC: 14, TABLE: 
		[[1, 20, d1, COMMON, CURATIVE], [21, 40, d1, COMMON, REACTIVE], [41, 60, d4, COMMON, CURATIVE],
		 [61, 80, d1, UNCOMMON, CURATIVE], [81, 99, d1, UNCOMMON, DIVINE], [100, 100, d1, UNCOMMON, DIVINE]]},
	'outer plane': {COLOR: "<color>", DC: 14, TABLE: 
		[[1, 20, d1, COMMON, REACTIVE], [21, 40, d1, COMMON, REACTIVE], [41, 60, d4, COMMON, REACTIVE],
   		 [61, 80, d1, UNCOMMON, REACTIVE], [81, 99, d1, UNCOMMON, ARCANE], [100, 100, d4, RARE, ARCANE]]},
				 
}

# Arguments
def parse_args(args):
    biome = "forest"
    count = 1

    arg_count = len(args)
    if arg_count > 0:
        biome = args[0].lower()
        
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
def biome_table_lookup(name):
	if name not in REAGENTS:
		return None
	return REAGENTS[name][TABLE]

def range_lookup(table, roll):
	for row in table:
		if row[0] <= roll <= row[1]: 
			return row
	return None

def color_lookup(name):
	if name not in REAGENTS:
		return "#FF0000"
	return REAGENTS[name][COLOR]

def roll_lookup(name, roll):
	table = biome_table_lookup(name)
	if table == None:
			# Later pull these from the table itself
			all_biomes = REAGENTS.keys()
			err(f"Could not find biome named '{name}'. Please choose from {', '.join(all_biomes)}.")
	
	t = range_lookup(table, roll)
	if t == None:
		return ["nothing"]
	d, r, v = t[DICE_INDEX], t[RARITY_INDEX], t[VARIETY_INDEX]
	c = vroll(d).total
	fname = r + " " + v 
	return [fname] * c

def remove_items(test_list, item):
	res = [i for i in test_list if i != item] 
	return res 

def foraged_display_name(foraged, count):
	if count == 0:
		return "No " + foraged + "s" # Should be impossible
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
    color = color_lookup(biome)
    title = f"{character().name} is gathering reagents in the {biome}."
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
