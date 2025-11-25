import sqlite3

conn = sqlite3.connect('coffee.sqlite')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS coffee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roast_degree TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    volume REAL NOT NULL
)
''')


conn.commit()
conn.close()
