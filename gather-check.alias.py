# Gather Check
#
# A standalone alias to perform a gather check.
# This will later be integrated into the `gather` alias`.
# 
# Usage:
# !gather-check materials 
# !gather-check reagents pro          # When gathering reagents, you can pass in 'pro', 'prof' or 'exp' if you have proficiency or epertise in the Herbalism Kit
# !gather-check game
# !gather-check materials adv         # Gather with advantage (or dis for disadvantage)
# !gather-check materials guidance    # Gather with guidance added
# !gather-check reagents pro adv guidance -b 1 # You can combine them
#
# Notes:
# - Will automatically use Herbalism Kit Proficiency & Expertise if the player is using Tool Check (https://avrae.io/dashboard/workshop/630b0e39b85ea38890666c08)
#   - Passing in pro or exp will override any Tool Check Values.
# - Gather checks automatically use the highest ability score, no need to pass any in.
# - When looking up Survival modifier, this automatically uses Jack of All Trades, Proficiency, and Expertise without needing to pass in any values

!alias gather-check echo <drac2>

REAGENTS, MATERIALS, GAME = "reagents", "materials", "game"
ALLOWED_GATHER_COMMANDS = [REAGENTS, MATERIALS, GAME]

def roll_for_skill(skill, args, addedBonus = None):
    ch = character()

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
    if strength >= dexterity and strength >= wisdom:
        return "strength"
    if dexterity >= strength and dexterity >= wisdom:
        return "dexterity"
    return "wisdom"

def best_hunting_stat():
    if dexterity > wisdom:
        return "dexterity"
    return "wisdom"

def herbalism_kit_proficiency_bonus(args):
    if "exp" in args:
        return "+" + 2 * proficiencyBonus

    if "pro" in args or if "prof" in args:
        return "+" + proficiencyBonus    
    
    # If neither 'pro' or 'exp' are in args, look for Tool Check values
    cvars = character().cvars
    if "eTools" in cvars and "Herbalism Kit" in cvars["eTools"]:
        return " +" + 2 * proficiencyBonus 
    
    if "pTools" in cvars and "Herbalism Kit" in cvars["pTools"]:
        return "+" + proficiencyBonus

    return None

def survival_proficiency_bonus():
    survival = character().skills["survival"]
    return "+ " + survival.prof * proficiencyBonus


def survival_modifier_bonus():
    survival = character().skills["survival"]
    if survival.prof >= 1:
        return "+ " + survival.value
    return None

def arg_parse_action_type(args):
    for action in ALLOWED_GATHER_COMMANDS:
        if action in args:
            return action
    return None

def skill_roll_for_action(action, args):
    if action == REAGENTS:
        return roll_for_skill("wisdom", args, herbalism_kit_proficiency_bonus(args))
    if action == MATERIALS:
        return roll_for_skill(best_searching_stat(), args, survival_proficiency_bonus())
    if action == GAME:
        return roll_for_skill(best_hunting_stat(), args, survival_modifier_bonus())
    return None

# Core Logic
a = argparse(&ARGS&)
action_name = arg_parse_action_type(a)
skill_roll = skill_roll_for_action(action_name, a)

if not skill_roll:
    return err(f"You must pass in what you are gathering. Expected values are ({', '.join(ALLOWED_GATHER_COMMANDS)})")

return f"{character().name} is gathering {action_name}.\n\n{skill_roll}"

</drac2>