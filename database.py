import sqlite3

conn = sqlite3.connect("apod.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS favorites (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT,

    date TEXT,

    image_url TEXT,

    explanation TEXT,

    media_type TEXT

)
""")

conn.commit()
conn.close()

print("Database and Table Created Successfully")