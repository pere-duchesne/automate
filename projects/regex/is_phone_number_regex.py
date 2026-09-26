#!/usr/bin/env python3
#Same simple program as in is_phone_number.py but with regex capture

import sys
import re

user_text='My phone number is 455-455-5665'

def is_phone_number(text):
    phone_regex=re.compile(r'\d{3}-\d{3}-\d{4}')
    phone=phone_regex.findall(text)
    print(phone)
    if not phone is None:
        return {'result':True,'phone':phone}
    else:
        return {'result':False,'phone':phone}

print(is_phone_number(user_text))
