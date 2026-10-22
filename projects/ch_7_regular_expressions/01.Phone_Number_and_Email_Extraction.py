#!/usr/bin/env python3
import re
import pyperclip

#Send some text to the clipboard and serach for phone numbers and email addresses, then replace the whole bunch of text by just the addresses

###Steps
#1: Get the off the clipboard
#2. Find addresses
#3. Paste them back to the clipboard
###Code structure
#1. Get the copied text with pyperclip library
#2. Two regular expressiones for numbers and email addresses
#3. Format the captured chunks of text
#4. If no matched strings were found display some message

phone_regex=re.compile(r'''(
(\d{3}|\(\d{3}\))? #optional area code
(\s|-|\.)? #optional separator
(\d{3}) #3 digits
(\s|-|\.)? #optional separator
(\d{4}) #4 digits
(\s*(ext|x|ext.)\s(\d{2,5}))? #optional extension
)''',re.VERBOSE)

#phone1='123 4564444'
#phone2='123-456 4444'
#phone3='123.456-4444'

#print(phone_regex.search(phone1))
#print(phone_regex.search(phone2))
#print(phone_regex.search(phone3))

email_regex=re.compile(r'''(
[a-zA-Z0-9.-_]* #address
@ #at symbol
[a-zA-Z0-9.-_]*\.\w{2,3} #domain
)''',re.VERBOSE)

#my_email='me@somedomain.me'
#your_email='your_address.something@else.com'

#print(email_regex.search(my_email))
#print(email_regex.search(your_email))

text=str(pyperclip.paste())

captured_phones=phone_regex.findall(text)
captured_phones=[cap[0] for cap in captured_phones]

captured_emails=email_regex.findall(text)
captured={'phones':captured_phones,'emails':captured_emails}

print(captured)
