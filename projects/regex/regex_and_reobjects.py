#!/usr/bin/env python3
#An overview of regex pbjects methods

import re

pattern=re.compile(r'\d+')

text='abs123'
number='123abs'

#.match() checks for match at the beginning of the string. If didn`t find any returns None
match_method_returns_none=pattern.match(text)
match_method_returns_match=pattern.match(number)

print(match_method_returns_none)
print(match_method_returns_match)
print(match_method_returns_match.group(0))

#.search() same as .match() ut search on the entire strings. Returns the first match or None

search_method_on_text=pattern.search(text)
print(search_method_on_text)

search_method_on_number=pattern.search(number)
print(search_method_on_number)

#.findall()
