#!/usr/bin/env python3
#A simple program showing how the pipe | works. It works like an "or" operator. Returns the matches that match with the first or the another expression
import re



hero_regex=re.compile(f'Batman|Tina Fey|Piluso')
batman='Batman and Tina Fey'
tina_fey='Tina Fey and Batman'
more_heroes='Tina Fey, Batman and Piluso'

#.search() returns the first found match match
batman_found=hero_regex.search(batman)
tina_fey_found=hero_regex.search(tina_fey)

print(f'First match being batman in the string {batman}: {batman_found}')
print(f'First match being tina_fey in the string {tina_fey}: {tina_fey_found}')


#.findall() returns a list with all the matches
batman_foundall=hero_regex.findall(batman)
tina_fey_foundall=hero_regex.findall(tina_fey)
all_heroes=hero_regex.findall(more_heroes)

print(f'All matches being batman or tina fey in the string {batman}: {batman_foundall}')
print(f'All matches being tina_fey or batman in the string {tina_fey}: {tina_fey_foundall}')
print(f'All matches in the string {more_heroes}: {all_heroes}')

#Matching all the expressions that share a prefix
a_shared_prefix_for_many=re.compile(r'Bat(man|mobile|copter|bat)')

string_expression='The Batmobile lost a wheel.'
string_expression_with_many='The Batmobile lost a wheel and Batman lost himself'

returns_batmobile=a_shared_prefix_for_many.search(string_expression)
returns_many=a_shared_prefix_for_many.findall(string_expression_with_many)

print(f'Returns one combination: {returns_batmobile.group()}')
print(f'Returns many combinations: {returns_many}')
