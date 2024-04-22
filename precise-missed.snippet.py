# Use this after a Precise Strike misses to restore your slot
# Usage: precice-missed

!snippet precice-missed embed
 <drac2>
char = character()
counter_name = "Squire of Solamnia: Precise Strike"
value = char.get_cc(counter_name)
if value < char.get_cc_max(counter_name):
  char.mod_cc(counter_name, +1)
  return f''' -f "{counter_name}|{char.cc_str(counter_name)} (+1)\n 
**Missed Precise Strike** Precise strikes are only expended if the attack hits, and you have restored one usage for the day." '''
else:
  return f''' -f "**Missed Precise Strike.** `precise-missed` cannot be used as **{counter_name}** is already full {char.cc_str(counter_name)}. Only use this command after you've missed an attack with the `precise` snippet." '''
</drac2>