#!/usr/bin/env python3
#A little python program to show how * and + work and its relationship with ?

import re

expression1='This is Batman'
expression2='This is the Batwoman mobile'
expression3='This is whatever with Batwowowowowoman'

asterisk=re.compile(r'Bat(wo)*man')
plus=re.compile(r'Bat(wo)+man')

print(f'{expression1}, asterisk matches {asterisk.search(expression1)}')
print(f'{expression1}, plus matches {plus.search(expression1)}')
