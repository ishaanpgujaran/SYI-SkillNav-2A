# setup_db.py
import sqlite3

# Connect to the database
conn = sqlite3.connect('skillnav.db')
c = conn.cursor()

# Create a table for resources
c.execute('''
    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        title TEXT ,
        creator TEXT,
        description TEXT,
        platform TEXT,
        duration TEXT,
        views TEXT,
        likes TEXT,
        published_on TEXT,
        link TEXT ,
        thumbnail TEXT,
        type TEXT,
        difficulty TEXT
        
    )
''')

conn.commit()
conn.close()
