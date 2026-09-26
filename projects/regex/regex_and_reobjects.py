#!/usr/bin/env python3
#An overview of regex pbjects methods

import re
import random


pattern=re.compile(r'\d+')

text='abs123'
number='123abs'

#.match() checks for match at the beginning of the string. If didn`t find any returns None
match_method_returns_none=pattern.match(text)
match_method_returns_match=pattern.match(number)

print(f'Match d+ on {text}: {match_method_returns_none}')
print(f'Match d+ on {number}: {match_method_returns_match}')

print(f'.group() on the match oject of {number} returns only the matched string: {match_method_returns_match.group()}')

#.search() same as .match() ut search on the entire strings. Returns the first match or None

search_method_on_text=pattern.search(text)
print(f'.search() on a match object of {text} returns the matched string wherever it happens: {search_method_on_text}')

#.findall() same as .search() but don`t stop at the first match. Returns a list with the matches or None

text_extended=text+'_'+number

findall_on_text_extended=pattern.findall(text_extended)
print(f'.findall() on a match object {text_extended} returns a list with the matched chunks: {findall_on_text_extended}')

#Collapse the chunks found with .findall()
print(f'Collpased .findall() from {findall_on_text_extended} list: {''.join(findall_on_text_extended)}')

#.group() Te regex can be grouped y introducing sugroups in the pattern

grouped_pattern=re.compile(r'(\d{3})-(\d{3}-\d{4})')

print(f'The grouped reobject is: {grouped_pattern}')

area_code=random.randint(100,999)
number1=random.randint(100,999)
number2=random.randint(1000,9999)
phone=str(area_code)+'-'+str(number1)+'-'+str(number2)

print(f'My phone number is {phone}')
group=grouped_pattern.search(phone)
print(f'Grouped Pattern:{group}')
print(f'.groups() to get the whole matched string group-tupled: {group.groups()}')
print(f'.group(0): {group.group(0)}; .group(1): {group.group(1)}; .group(2): {group.group(2)}')

#re.sub() on a text replaces the matched string with another. Takes: pattern, replace_text, arch_text
replace=re.sub(pattern, phone, text)
print(f'Replace the numbers in {text} with value of {phone}: {replace}')

