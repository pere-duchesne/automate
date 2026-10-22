#!/usr/bin/env python3
#A program to check whether a text is a phone number or not

import sys

user=sys.argv[1]

def is_phone_number(text):
    if len(text)!=12:
        return False
    hyphens=[3,7]
    pos_hyphens=''.join(text[_] for _ in hyphens)
    if pos_hyphens!='--':
        return False
    if not (text[0:2].isdecimal() or text[4:6].isdecimal() or text[8:11].isdecimal()):
        return False
    return True

results=[]
chunks=[]

for i in range(len(user)):
    chunk=user[i:i+12]
    result=is_phone_number(chunk)
    results.append(result)
    chunks.append(chunk)
    if result:
        print(f'{chunk}: phone number found @{i+1}:{i+12}')
how_many=sum(results)
if how_many==0:
    print(f'{how_many} phone numbers found')
elif how_many==1:
    print(f'{how_many} phone number found')
else:
    print(f'{how_many} phone numbers found')


print('Job done!')

#The program has a flaw: if we write a phone number with more than 4 digits after second hyphen
print(chunks)
