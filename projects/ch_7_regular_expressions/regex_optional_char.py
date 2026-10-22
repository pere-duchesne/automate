#!/usr/bin/env python3
#A simple program that shows how to use question mark for optional matching
#Optional match: a set of characters that you want to match only optionally
#i.e: f'Bat(wo)?man'

import re

pattern=re.compile(r'Bat(wo)?man')
expression1='The adventures of Batwoman'
expression2='The adventures of Batman'

batwoman=pattern.search(expression1)
batman=pattern.search(expression2)

print(f'{expression1}, {batwoman}')
print(f'{expression2}, {batman}')

matched_text={expression1:batwoman.group(),expression2:batman.group()}
print(matched_text)

#Phone number regexp example with question marks

phone_pattern=re.compile(r'(\d{3}-)?\d{3}-\d{4}')
phone1='me number is 415-555-4242'
phone2='me number is 555-4242'

match1=phone_pattern.search(phone1).group()
match2=phone_pattern.search(phone2).group()

print(f'{phone_pattern} matchs this: {phone1}: {match1}')
print(f'{phone_pattern} matchs this: {phone2}: {match2}')
