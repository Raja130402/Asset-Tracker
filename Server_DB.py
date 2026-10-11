
import sqlite3


def create_server_table():

    conn = sqlite3.connect("Add_components.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servers (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            product_id TEXT UNIQUE,

            server_name TEXT,

            brand TEXT,

            model TEXT,

            serial_number TEXT,

            cpu TEXT,

            cpu_cores TEXT,

            ram TEXT,

            storage TEXT,

            storage_type TEXT,

            raid TEXT,

            operating_system TEXT,

            os_version TEXT,

            hostname TEXT,

            ip_address TEXT,

            mac_address TEXT,

            management_ip TEXT,

            data_center TEXT,

            rack TEXT,

            rack_position TEXT,

            assigned_to TEXT,

            condition TEXT,

            status TEXT,

            warranty TEXT,

            remarks TEXT

        )
    """)

    conn.commit()

    conn.close()


if __name__ == "__main__":

    create_server_table()

    print("Server table created successfully.")

