import sqlite3


# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect("Add_components.db")
cursor = conn.cursor()


# =========================================================
# CREATE LAPTOPS TABLE
# =========================================================

cursor.execute("""
    CREATE TABLE IF NOT EXISTS laptops
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        asset_id INTEGER UNIQUE NOT NULL,

        processor TEXT,
        cpu_cores TEXT,

        ram TEXT,

        storage TEXT,
        storage_type TEXT,

        display_size TEXT,

        operating_system TEXT,
        os_version TEXT,

        hostname TEXT,

        ip_address TEXT,
        mac_address TEXT,

        battery_health TEXT
    )
""")


# =========================================================
# SAVE
# =========================================================

conn.commit()

conn.close()

print("Laptops table created successfully.")