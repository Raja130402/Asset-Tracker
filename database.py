import sqlite3

conn = sqlite3.connect("Add_components.db")

conn.execute("""
CREATE TABLE Add_components(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list Text,
    Brand TEXT,
    Model TEXT,
    seriel TEXT,
    seating_no TEXT,
    Assigned_to TEXT, 
    location TEXT,
    license TEXT,
    condition TEXT

  
    

)
""")

conn.commit()
conn.close()
print("db create")