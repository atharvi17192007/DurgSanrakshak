import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'durgsanrakshak.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema_sqlite.sql')

connection = sqlite3.connect(DB_PATH)

with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
    schema_sql = f.read()

connection.executescript(schema_sql)
connection.commit()
connection.close()

print("SUCCESS: durgsanrakshak.db tayar zala, sagle tables banle!")
