import sqlite3
from flask import g

DATABASE = 'soknader.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS soknader (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            navn_forelder_1 TEXT,
            prioriterte_barnehager TEXT,
            resultat TEXT,
            valgt_barnehage TEXT
        )
    ''')
    db.commit()
