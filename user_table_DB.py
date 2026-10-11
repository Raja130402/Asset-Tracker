import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Employee_code TEXT,
    Employee_name TEXT,
    TL_name TEXT,
    Team_name TEXT,
    Assigned_asset TEXT,
    Location TEXT
)
""")

conn.commit()
conn.close()

print("Users table created successfully!")