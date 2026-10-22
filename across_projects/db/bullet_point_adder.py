#!/usr/bin/env python3
#a simple program that takes text copied to the clipboard, process it and copy it back to the clipboard

import pyperclip

text=pyperclip.paste()
texts=text.split('\n')

texts=['* '+text for text in texts]
final_list_of_texts='\n'.join(texts)

pyperclip.copy(final_list_of_texts)
