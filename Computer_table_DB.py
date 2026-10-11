import sqlite3

conn = sqlite3.connect("Add_components.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS computers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    processor TEXT,
    cpu_cores TEXT,
    ram TEXT,
    storage TEXT,
    storage_type TEXT,
    operating_system TEXT,
    os_version TEXT,
    hostname TEXT,
    ip_address TEXT,
    mac_address TEXT,
    FOREIGN KEY (asset_id) REFERENCES assets(id)
)
""")

conn.commit()
conn.close()

print("Computers table created successfully.")