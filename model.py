import sqlite3
import os
import sys

def get_database_path():
    if getattr(sys, 'frozen', False):
        # Если запущено как exe
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, 'data', 'coffee.sqlite')

db_path = get_database_path()
os.makedirs(os.path.dirname(db_path), exist_ok=True)

conn = sqlite3.connect(db_path)
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

cursor.execute("DELETE FROM coffee")

coffee_data = [
    ('Эфиопия Иргачефф', 'Средняя', 'Зерна', 'Цветочные и цитрусовые ноты с яркой кислотностью', 1250.0, 250.0),
    ('Колумбия Супремо', 'Темная', 'Молотый', 'Шоколадный вкус с ореховыми нотами', 980.0, 250.0),
    ('Кения АА', 'Светлая', 'Зерна', 'Ягодные тона с винным послевкусием', 1450.0, 200.0),
    ('Бразилия Сантос', 'Средняя', 'Молотый', 'Ореховый вкус с сладким карамельным послевкусием', 850.0, 500.0),
    ('Гватемала Антивей', 'Темная', 'Зерна', 'Дымный аромат с пряными нотами', 1100.0, 300.0),
    ('Эспрессо Бленд', 'Темная', 'Молотый', 'Сбалансированный вкус для эспрессо', 920.0, 400.0),
    ('Коста Рика Тарразу', 'Средняя', 'Зерна', 'Яркий вкус с нотками карамели и орехов', 1350.0, 250.0)
]

cursor.executemany('''
INSERT INTO coffee (name, roast_degree, type, description, price, volume)
VALUES (?, ?, ?, ?, ?, ?)
''', coffee_data)

conn.commit()
conn.close()