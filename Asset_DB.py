import sqlite3

conn = sqlite3.connect("Add_components.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT UNIQUE,
    asset_category TEXT NOT NULL,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    serial_number TEXT NOT NULL,
    assigned_to TEXT,
    location TEXT,
    seating_no TEXT,
    condition TEXT NOT NULL,
    status TEXT,
    warranty TEXT,
    license TEXT,
    remarks TEXT
)
""")

conn.commit()
conn.close()

print("Assets table created successfully.")