#! /usr/bin/env python3
#a simple database table for keeping track on what I am on everyday

import sqlite3
from dotenv import load_dotenv
import os

load_dotenv(override=True)
DB_PATH=os.getenv('SQLITE_PATH')

what=input('What do you want to do? Retrieve(r)/Input(i)\n')
if what =='i':
    print('Prepared for input mode...')
    with sqlite3.connect(DB_PATH) as conn:
        cursor=conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_notebook (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            content TEXT,
            topic TEXT,
            minutes INTEGER,
            comment TEXT,
            date TEXT DEFAULT (date('now')),
            created TEXT DEFAULT (datetime('now')));
        """)
        cursor.execute("PRAGMA table_info(learning_notebook)")
        columns=cursor.fetchall()
        values_to_insert={}
        for column in columns[1:6]:
            if column[1]=='category':
                ie='algebra, history, math, calculus, etc.'
            elif column[1]=='content':
                ie='ck12 precalculus, das kapital, etc.'
            elif column[1]=='topic':
                ie='polynomials, complex numbers, money as capital, etc.'
            elif column[1]=='minutes':
                ie='just put a positive integer representing the minutes dedidated to the topic.'
            else:
                ie='try to explain the goal, give a quick summarisation, etc.'
            user=input(f'Input {column[1]} (ie.: {ie}):\n')
            values_to_insert[column[1]]=(int(user) if column[1]=='minutes' else user)
       
        column_names=', '.join(values_to_insert.keys())
        placeholders=', '.join('?' for _ in values_to_insert)
        sql=f'INSERT INTO learning_notebook ({column_names}) VALUES ({placeholders})'
        cursor.execute(sql, tuple(values_to_insert.values()))
        print(f'New entry {values_to_insert} inserted into the database.\nBye.')




