#!/usr/bin/env python3
#An insecure password locker program.

import sqlite3
import sys
import os
from dotenv import load_dotenv

load_dotenv(override=True)
DB_PATH=os.getenv('SQLITE_PATH')

if len(sys.argv)<2:
    print('Usage: python pw.py [account] - copy account password')
else:
    user_value=sys.argv[1]
    with sqlite3.connect(DB_PATH) as conn:
        cursor=conn.cursor()
        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS passwords (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        account TEXT,
                        password TEXT,
                        created_at TEXT DEFAULT (datetime('now')));
                        """)
        cursor.execute("Select account, password from passwords where account=?;",(user_value,))
        result=cursor.fetchone()
        if result is None:
            response=input('Nothin\' in the Database. Wanna create an account? yes(y)/no(n)\n')
            if response=='y':
                password=input('Enter new account\'s password:\n')
                values=(user_value, password)
                cursor.execute("""
                    INSERT INTO passwords (account, password)
                        VALUES(?,?)
                        """, values)
                print(f'Account {user_value} successfully created!')
            else:
                print('Ok. Bye!')
        else:
            import pyperclip
            pyperclip.copy(result[1])
            print(f'Password for {user_value} copied to clipboard!')
