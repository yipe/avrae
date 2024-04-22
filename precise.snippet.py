# Use this to make a precise strike as a Squire of Solamnia
# Usage: !a <weapon_name> precise -t <target_name>

!snippet precise <drac2>
char = character()
counter_name = "Squire of Solamnia: Precise Strike"
value = char.get_cc(counter_name)
if value:
  char.mod_cc(counter_name, -1)
  return f''' -f "{counter_name}|{char.cc_str(counter_name)} (-1)\n 
**Precise Strike.** Once per turn, when you make a weapon attack roll against a creature, you can cause the attack roll to have advantage. If the attack hits, you roll a d8 and add the number rolled as a bonus to the attack's damage roll. You can use this benefit a number of times equal to your proficiency bonus, but a use is expended only if the attack hits. You regain all expended uses when you finish a long rest." '''
else:
  err(f"No uses of {counter_name} remaining!")
</drac2>
-d 1d8 adv