#!/usr/bin/env python3
#Using {} to match many repetitions of a pattern. This was seen when matching phone numbers with \d{3}-. Now we`re going to see an extention to that

import re

pattern_single=re.compile(r'(Ha){5}')
pattern_multi=re.compile(r'(Ha){3,5}')
pattern_zero_or_many=re.compile(r'Ha{,5}')

Ha=['Ha'*n for n in range(1,6)]

for h in Ha:
    print(f'char:{h}, pattern:{pattern_single}, returns:{pattern_single.search(h)}')
    print(f'char:{h}, pattern:{pattern_multi}, returns:{pattern_multi.search(h)}')
    print(f'char:{h}, pattern:{pattern_zero_or_many}, returns:{pattern_zero_or_many.findall(h)}')
