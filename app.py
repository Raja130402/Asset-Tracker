from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_file
)

from openpyxl import Workbook

import sqlite3
import os


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)


# =========================================================
# DATABASE HELPER
# =========================================================

def get_db_connection(database):
    conn = sqlite3.connect(database)
    return conn


# =========================================================
# LOGIN
# =========================================================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username", ""
        ).strip()

        password = request.form.get(
            "password", ""
        ).strip()

        if username == "admin" and password == "123":

            return redirect(
                url_for("adminpage")
            )

    return render_template(
        "loginpage.html"
    )


# =========================================================
# ADMIN PAGE
# =========================================================

@app.route("/adminpage")
def adminpage():

    return render_template(
        "adminpage.html"
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    conn = get_db_connection(
        "Add_components.db"
    )

    cursor = conn.cursor()

    try:

        # -------------------------------------------------
        # TOTAL ASSETS
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM assets
        """)

        total_assets = cursor.fetchone()[0]


        # -------------------------------------------------
        # GOOD ASSETS
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM assets
            WHERE LOWER(TRIM(condition)) = 'good'
        """)

        good_assets = cursor.fetchone()[0]


        # -------------------------------------------------
        # DAMAGED ASSETS
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM assets
            WHERE LOWER(TRIM(condition)) = 'damaged'
        """)

        damaged_assets = cursor.fetchone()[0]


        # -------------------------------------------------
        # ASSIGNED ASSETS
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM assets
            WHERE assigned_to IS NOT NULL
            AND TRIM(assigned_to) != ''
        """)

        assigned_assets = cursor.fetchone()[0]

    finally:

        conn.close()


    return render_template(
        "dashboard.html",
        total_assets=total_assets,
        good_assets=good_assets,
        damaged_assets=damaged_assets,
        assigned_assets=assigned_assets
    )


# =========================================================
# SYSTEM DETAILS / ASSET CATEGORIES
# =========================================================

@app.route("/system_details")
def system_details():

    return render_template(
        "system_details.html"
    )


# =========================================================
# COMPONENTS TABLE
#
# Old/common asset table
# =========================================================

@app.route("/components_table")
def components_table():

    option = request.args.get(
        "option", ""
    ).strip()


    conn = get_db_connection(
        "Add_components.db"
    )

    cursor = conn.cursor()

    try:

        if option:

            cursor.execute("""
                SELECT
                    product_id,
                    id,
                    asset_category,
                    brand,
                    model,
                    serial_number,
                    seating_no,
                    assigned_to,
                    location,
                    license,
                    condition

                FROM assets

                WHERE asset_category = ?

                ORDER BY id
            """, (option,))

        else:

            cursor.execute("""
                SELECT
                    product_id,
                    id,
                    asset_category,
                    brand,
                    model,
                    serial_number,
                    seating_no,
                    assigned_to,
                    location,
                    license,
                    condition

                FROM assets

                ORDER BY id
            """)

        data = cursor.fetchall()

    finally:

        conn.close()


    return render_template(
        "components_table.html",
        data=data,
        selected_category=option
    )


# =========================================================
# DELETE COMPONENT
# =========================================================

@app.route("/delete/<int:id>")
def delete(id):

    conn = get_db_connection(
        "Add_components.db"
    )

    cursor = conn.cursor()

    try:

        cursor.execute("""
            DELETE FROM assets
            WHERE id = ?
        """, (id,))

        conn.commit()

    except sqlite3.Error as e:

        conn.rollback()

        return (
            f"Database Error: {e}",
            500
        )

    finally:

        conn.close()


    return redirect(
        url_for("components_table")
    )


# =========================================================
# EDIT COMPONENT
# =========================================================

@app.route("/edit/<int:id>")
def edit(id):

    conn = get_db_connection(
        "Add_components.db"
    )

    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                id,
                product_id,
                asset_category,
                brand,
                model,
                serial_number,
                seating_no,
                assigned_to,
                location,
                license,
                condition

            FROM assets

            WHERE id = ?
        """, (id,))

        asset = cursor.fetchone()

    finally:

        conn.close()


    if asset is None:

        return (
            "Asset not found.",
            404
        )


    # -----------------------------------------------------
    # LOAD USERS
    # -----------------------------------------------------

    user_conn = get_db_connection(
        "users.db"
    )

    user_cursor = user_conn.cursor()

    try:

        user_cursor.execute("""
            SELECT
                Employee_code,
                Employee_name

            FROM users

            ORDER BY Employee_name
        """)

        users = user_cursor.fetchall()

    finally:

        user_conn.close()


    return render_template(
        "Add_components.html",
        asset=asset,
        users=users
    )


# =========================================================
# ADD / CREATE COMPONENT
# =========================================================

@app.route(
    "/Add_components",
    methods=["GET", "POST"]
)
def Add_components():

    # -----------------------------------------------------
    # LOAD USERS
    # -----------------------------------------------------

    user_conn = get_db_connection(
        "users.db"
    )

    user_cursor = user_conn.cursor()

    try:

        user_cursor.execute("""
            SELECT
                Employee_code,
                Employee_name

            FROM users

            ORDER BY Employee_name
        """)

        users = user_cursor.fetchall()

    finally:

        user_conn.close()


    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    if request.method == "GET":

        return render_template(
            "Add_components.html",
            users=users
        )


    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    category = request.form.get(
        "list", ""
    ).strip()

    brand = request.form.get(
        "Brand", ""
    ).strip()

    model = request.form.get(
        "Model", ""
    ).strip()

    seriel = request.form.get(
        "seriel", ""
    ).strip()

    seating_no = request.form.get(
        "seating_no", ""
    ).strip()

    assigned_to = request.form.get(
        "Assigned_To", ""
    ).strip()

    location = request.form.get(
        "location", ""
    ).strip()

    license_value = request.form.get(
        "license", ""
    ).strip()

    condition = request.form.get(
        "condition", ""
    ).strip()


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    required_fields = {

        "Category": category,

        "Brand": brand,

        "Model": model,

        "Serial Number": seriel,

        "Location": location,

        "Condition": condition

    }


    missing_fields = [

        field
        for field, value in required_fields.items()
        if not value

    ]


    if missing_fields:

        return render_template(
            "Add_components.html",
            error="Please fill all required fields.",
            missing_fields=missing_fields,
            users=users
        )


    # -----------------------------------------------------
    # DATABASE
    # -----------------------------------------------------

    conn = get_db_connection(
        "Add_components.db"
    )

    cursor = conn.cursor()


    try:

        # -------------------------------------------------
        # GENERATE PRODUCT ID
        # -------------------------------------------------

        cursor.execute("""
            SELECT product_id

            FROM assets

            WHERE asset_category = ?

            ORDER BY id DESC

            LIMIT 1
        """, (category,))

        last = cursor.fetchone()


        next_number = 1


        if last and last[0]:

            last_product_id = str(
                last[0]
            ).strip()

            number_part = (
                last_product_id
                .split("_")[-1]
            )

            if number_part.isdigit():

                next_number = (
                    int(number_part) + 1
                )


        product_id = (
            f"{category.upper()}_{next_number:03d}"
        )


        # -------------------------------------------------
        # INSERT ASSET
        # -------------------------------------------------

        cursor.execute("""
            INSERT INTO assets
            (
                product_id,
                asset_category,
                brand,
                model,
                serial_number,
                seating_no,
                assigned_to,
                location,
                license,
                condition
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (

            product_id,

            category,

            brand,

            model,

            seriel,

            seating_no,

            assigned_to,

            location,

            license_value,

            condition

        ))


        conn.commit()


    except sqlite3.Error as e:

        conn.rollback()

        return render_template(
            "Add_components.html",
            error=f"Database Error: {e}",
            users=users
        )


    finally:

        conn.close()


    return render_template(
        "Add_components.html",
        success=(
            f"Asset {product_id} "
            f"added successfully."
        ),
        users=users
    )


# =========================================================
# UPDATE COMPONENT
# =========================================================

@app.route(
    "/update_component/<int:id>",
    methods=["POST"]
)
def update_component(id):

    assigned_to = request.form.get(
        "Assigned_To", ""
    ).strip()

    location = request.form.get(
        "location", ""
    ).strip()

    condition = request.form.get(
        "condition", ""
    ).strip()


    conn = get_db_connection(
        "Add_components.db"
    )

    cursor = conn.cursor()


    try:

        cursor.execute("""
            UPDATE assets

            SET assigned_to = ?,
                location = ?,
                condition = ?

            WHERE id = ?

        """, (

            assigned_to,

            location,

            condition,

            id

        ))


        conn.commit()


    except sqlite3.Error as e:

        conn.rollback()

        return (
            f"Database Error: {e}",
            500
        )

    finally:

        conn.close()


    return redirect(
        url_for("components_table")
    )


# =========================================================
# COMPONENT HISTORY
# =========================================================

@app.route("/components_histroy")
def components_histroy():

    return render_template(
        "components_histroy.html"
    )


# =========================================================
# USER DETAILS
# =========================================================

@app.route("/user_details")
def user_details():

    return render_template(
        "User_details.html"
    )


# =========================================================
# ADD COMPUTER
# =========================================================

@app.route(
    "/add_computer",
    methods=["GET", "POST"]
)
def add_computer():

    # -----------------------------------------------------
    # LOAD USERS
    # -----------------------------------------------------

    user_conn = get_db_connection(
        "users.db"
    )

    user_cursor = user_conn.cursor()

    try:

        user_cursor.execute("""
            SELECT
                Employee_code,
                Employee_name

            FROM users

            ORDER BY Employee_name
        """)

        users = user_cursor.fetchall()

    finally:

        user_conn.close()


    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    if request.method == "GET":

        return render_template(
            "Add_computer.html",
            users=users
        )


    # -----------------------------------------------------
    # COMMON FIELDS
    # -----------------------------------------------------

    brand = request.form.get(
        "brand", ""
    ).strip()

    model = request.form.get(
        "model", ""
    ).strip()

    serial_number = request.form.get(
        "serial_number", ""
    ).strip()

    assigned_to = request.form.get(
        "assigned_to", ""
    ).strip()

    location = request.form.get(
        "location", ""
    ).strip()

    seating_no = request.form.get(
        "seating_no", ""
    ).strip()

    condition = request.form.get(
        "condition", ""
    ).strip()

    status = request.form.get(
        "status", ""
    ).strip()

    warranty = request.form.get(
        "warranty", ""
    ).strip()

    license_value = request.form.get(
        "license", ""
    ).strip()

    remarks = request.form.get(
        "remarks", ""
    ).strip()


    # -----------------------------------------------------
    # COMPUTER FIELDS
    # -----------------------------------------------------

    processor = request.form.get(
        "processor", ""
    ).strip()

    cpu_cores = request.form.get(
        "cpu_cores", ""
    ).strip()

    ram = request.form.get(
        "ram", ""
    ).strip()

    storage = request.form.get(
        "storage", ""
    ).strip()

    storage_type = request.form.get(
        "storage_type", ""
    ).strip()

    operating_system = request.form.get(
        "operating_system", ""
    ).strip()

    os_version = request.form.get(
        "os_version", ""
    ).strip()

    hostname = request.form.get(
        "hostname", ""
    ).strip()

    ip_address = request.form.get(
        "ip_address", ""
    ).strip()

    mac_address = request.form.get(
        "mac_address", ""
    ).strip()


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    required_fields = {

        "Brand": brand,

        "Model": model,

        "Serial Number": serial_number,

        "Location": location,

        "Processor": processor,

        "RAM": ram,

        "Storage": storage,

        "Operating System": operating_system

    }


    missing_fields = [

        field
        for field, value in required_fields.items()
        if not value

    ]


    if missing_fields:

        return render_template(
            "Add_computer.html",
            error="Please fill all required fields.",
            missing_fields=missing_fields,
            users=users
        )


    # -----------------------------------------------------
    # DATABASE
    # -----------------------------------------------------

    conn = get_db_connection(
        "Add_components.db"
    )

    cursor = conn.cursor()


    try:

        # -------------------------------------------------
        # GENERATE COMPUTER PRODUCT ID
        # -------------------------------------------------

        cursor.execute("""
            SELECT product_id

            FROM assets

            WHERE asset_category = ?

            ORDER BY id DESC

            LIMIT 1
        """, ("Computer",))

        last = cursor.fetchone()


        next_number = 1


        if last and last[0]:

            last_product_id = str(
                last[0]
            ).strip()

            number_part = (
                last_product_id
                .split("_")[-1]
            )

            if number_part.isdigit():

                next_number = (
                    int(number_part) + 1
                )


        product_id = (
            f"COMPUTER_{next_number:03d}"
        )


        # -------------------------------------------------
        # INSERT COMMON ASSET
        # -------------------------------------------------

        cursor.execute("""
            INSERT INTO assets
            (
                product_id,
                asset_category,
                brand,
                model,
                serial_number,
                assigned_to,
                location,
                seating_no,
                condition,
                status,
                warranty,
                license,
                remarks
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (

            product_id,

            "Computer",

            brand,

            model,

            serial_number,

            assigned_to,

            location,

            seating_no,

            condition,

            status,

            warranty,

            license_value,

            remarks

        ))


        asset_id = cursor.lastrowid


        # -------------------------------------------------
        # INSERT COMPUTER DETAILS
        # -------------------------------------------------

        cursor.execute("""
            INSERT INTO computers
            (
                asset_id,
                processor,
                cpu_cores,
                ram,
                storage,
                storage_type,
                operating_system,
                os_version,
                hostname,
                ip_address,
                mac_address
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (

            asset_id,

            processor,

            cpu_cores,

            ram,

            storage,

            storage_type,

            operating_system,

            os_version,

            hostname,

            ip_address,

            mac_address

        ))


        conn.commit()


    except sqlite3.Error as e:

        conn.rollback()

        return render_template(
            "Add_computer.html",
            error=f"Database Error: {e}",
            users=users
        )


    finally:

        conn.close()


    return render_template(
        "Add_computer.html",
        success=(
            f"Computer {product_id} "
            f"added successfully."
        ),
        users=users
    )

# =========================================================
# ADD LAPTOP
# =========================================================

@app.route("/add_laptop", methods=["GET", "POST"])
def add_laptop():

    # =====================================================
    # LOAD USERS
    # =====================================================

    user_conn = get_db_connection("users.db")
    user_cursor = user_conn.cursor()

    try:

        user_cursor.execute("""
            SELECT
                Employee_code,
                Employee_name
            FROM users
            ORDER BY Employee_name
        """)

        users = user_cursor.fetchall()

    finally:

        user_conn.close()


    # =====================================================
    # GET
    # =====================================================

    if request.method == "GET":

        return render_template(
            "Add_laptop.html",
            users=users
        )


    # =====================================================
    # COMMON ASSET FIELDS
    # =====================================================

    brand = request.form.get(
        "brand", ""
    ).strip()

    model = request.form.get(
        "model", ""
    ).strip()

    serial_number = request.form.get(
        "serial_number", ""
    ).strip()

    assigned_to = request.form.get(
        "assigned_to", ""
    ).strip()

    location = request.form.get(
        "location", ""
    ).strip()

    seating_no = request.form.get(
        "seating_no", ""
    ).strip()

    condition = request.form.get(
        "condition", ""
    ).strip()

    status = request.form.get(
        "status", ""
    ).strip()

    warranty = request.form.get(
        "warranty", ""
    ).strip()

    license_value = request.form.get(
        "license", ""
    ).strip()

    remarks = request.form.get(
        "remarks", ""
    ).strip()


    # =====================================================
    # LAPTOP FIELDS
    # =====================================================

    processor = request.form.get(
        "processor", ""
    ).strip()

    cpu_cores = request.form.get(
        "cpu_cores", ""
    ).strip()

    ram = request.form.get(
        "ram", ""
    ).strip()

    storage = request.form.get(
        "storage", ""
    ).strip()

    storage_type = request.form.get(
        "storage_type", ""
    ).strip()

    display_size = request.form.get(
        "display_size", ""
    ).strip()

    operating_system = request.form.get(
        "operating_system", ""
    ).strip()

    os_version = request.form.get(
        "os_version", ""
    ).strip()

    hostname = request.form.get(
        "hostname", ""
    ).strip()

    ip_address = request.form.get(
        "ip_address", ""
    ).strip()

    mac_address = request.form.get(
        "mac_address", ""
    ).strip()

    battery_health = request.form.get(
        "battery_health", ""
    ).strip()


    # =====================================================
    # VALIDATION
    # =====================================================

    required_fields = {

        "Brand": brand,

        "Model": model,

        "Serial Number": serial_number,

        "Location": location,

        "Processor": processor,

        "RAM": ram,

        "Storage": storage,

        "Operating System": operating_system

    }


    missing_fields = [

        field
        for field, value in required_fields.items()
        if not value

    ]


    if missing_fields:

        return render_template(
            "Add_laptop.html",
            error="Please fill all required fields.",
            missing_fields=missing_fields,
            users=users
        )


    # =====================================================
    # DATABASE
    # =====================================================

    conn = get_db_connection(
        "Add_components.db"
    )

    cursor = conn.cursor()


    try:

        # =================================================
        # GENERATE LAPTOP PRODUCT ID
        # =================================================

        cursor.execute("""
            SELECT
                product_id
            FROM assets
            WHERE asset_category = ?
            ORDER BY id DESC
            LIMIT 1
        """, ("Laptop",))

        last = cursor.fetchone()


        next_number = 1


        if last and last[0]:

            last_product_id = str(
                last[0]
            ).strip()

            number_part = (
                last_product_id
                .split("_")[-1]
            )

            if number_part.isdigit():

                next_number = (
                    int(number_part) + 1
                )


        product_id = (
            f"LAPTOP_{next_number:03d}"
        )


        # =================================================
        # INSERT COMMON ASSET
        # =================================================

        cursor.execute("""
            INSERT INTO assets
            (
                product_id,
                asset_category,
                brand,
                model,
                serial_number,
                assigned_to,
                location,
                seating_no,
                condition,
                status,
                warranty,
                license,
                remarks
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            product_id,

            "Laptop",

            brand,

            model,

            serial_number,

            assigned_to,

            location,

            seating_no,

            condition,

            status,

            warranty,

            license_value,

            remarks

        ))


        # =================================================
        # GET ASSET ID
        # =================================================

        asset_id = cursor.lastrowid


        # =================================================
        # INSERT LAPTOP DETAILS
        # =================================================

        cursor.execute("""
            INSERT INTO laptops
            (
                asset_id,
                processor,
                cpu_cores,
                ram,
                storage,
                storage_type,
                display_size,
                operating_system,
                os_version,
                hostname,
                ip_address,
                mac_address,
                battery_health
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            asset_id,

            processor,

            cpu_cores,

            ram,

            storage,

            storage_type,

            display_size,

            operating_system,

            os_version,

            hostname,

            ip_address,

            mac_address,

            battery_health

        ))


        # =================================================
        # SAVE
        # =================================================

        conn.commit()


    except sqlite3.Error as e:

        conn.rollback()

        return render_template(
            "Add_laptop.html",
            error=f"Database Error: {e}",
            users=users
        )


    finally:

        conn.close()


    # =====================================================
    # SUCCESS
    # =====================================================

    return render_template(
        "Add_laptop.html",
        success=(
            f"Laptop {product_id} "
            f"added successfully."
        ),
        users=users
    )

# =========================================================
# LAPTOP DETAILS
# =========================================================

@app.route("/laptop_details/<int:id>")
def laptop_details(id):

    conn = get_db_connection("Add_components.db")
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                a.id,
                a.product_id,
                a.asset_category,
                a.brand,
                a.model,
                a.serial_number,
                a.assigned_to,
                a.location,
                a.seating_no,
                a.condition,
                a.status,
                a.warranty,
                a.license,
                a.remarks,

                l.processor,
                l.cpu_cores,
                l.ram,
                l.storage,
                l.storage_type,
                l.display_size,
                l.operating_system,
                l.os_version,
                l.hostname,
                l.ip_address,
                l.mac_address,
                l.battery_health

            FROM assets a

            LEFT JOIN laptops l
                ON a.id = l.asset_id

            WHERE a.id = ?

        """, (id,))

        laptop = cursor.fetchone()

    finally:

        conn.close()


    if not laptop:

        return "Laptop not found", 404


    return render_template(
        "laptop_details.html",
        laptop=laptop
    )
    # =====================================================
    # LOAD USERS
    # =====================================================

    user_conn = get_db_connection("users.db")
    user_cursor = user_conn.cursor()

    try:

        user_cursor.execute("""
            SELECT
                Employee_code,
                Employee_name
            FROM users
            ORDER BY Employee_name
        """)

        users = user_cursor.fetchall()

    finally:

        user_conn.close()


    # =====================================================
    # GET
    # =====================================================

    if request.method == "GET":

        return render_template(
            "Add_laptop.html",
            users=users
        )
# =========================================================
# LAPTOP ASSETS
# =========================================================

@app.route("/laptop_assets")
def laptop_assets():

    conn = get_db_connection("Add_components.db")
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                a.id,
                a.product_id,
                a.asset_category,
                a.brand,
                a.model,
                a.serial_number,
                a.assigned_to,
                a.location,
                a.condition,
                a.status,

                l.processor,
                l.ram,
                l.storage,
                l.operating_system,
                l.display_size

            FROM assets a

            LEFT JOIN laptops l
                ON a.id = l.asset_id

            WHERE a.asset_category = 'Laptop'

            ORDER BY a.id DESC
        """)

        laptops = cursor.fetchall()

    finally:

        conn.close()

    return render_template(
        "laptop_assets.html",
        laptops=laptops
    )


# =========================================================
# COMPUTER ASSETS
# =========================================================

@app.route("/computer_assets")
def computer_assets():

    conn = get_db_connection(
        "Add_components.db"
    )

    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                a.id,
                a.product_id,
                a.asset_category,
                a.brand,
                a.model,
                a.serial_number,
                a.assigned_to,
                a.location,
                a.condition,
                a.status,

                c.processor,
                c.ram,
                c.storage,
                c.operating_system,
                c.hostname,
                c.ip_address

            FROM assets a

            LEFT JOIN computers c
                ON a.id = c.asset_id

            WHERE a.asset_category = ?

            ORDER BY a.id DESC

        """, ("Computer",))

        computers = cursor.fetchall()

    finally:

        conn.close()


    return render_template(
        "computer_assets.html",
        computers=computers
    )


@app.route("/computer_details/<int:id>")
def computer_details(id):

    conn = get_db_connection("Add_components.db")
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                a.id,
                a.product_id,
                a.asset_category,
                a.brand,
                a.model,
                a.serial_number,
                a.assigned_to,
                a.location,
                a.seating_no,
                a.condition,
                a.status,
                a.warranty,
                a.license,
                a.remarks,

                c.processor,
                c.cpu_cores,
                c.ram,
                c.storage,
                c.storage_type,
                c.operating_system,
                c.os_version,
                c.hostname,
                c.ip_address,
                c.mac_address

            FROM assets a

            LEFT JOIN computers c
                ON a.id = c.asset_id

            WHERE a.id = ?

        """, (id,))

        computer = cursor.fetchone()

    finally:
        conn.close()

    if not computer:
        return "Computer not found", 404

    return render_template(
        "computer_details.html",
        computer=computer
    )


# =========================================================
# SERVER ASSETS
# =========================================================

@app.route("/server_assets")
def server_assets():

    conn = get_db_connection("Add_components.db")
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                id,
                product_id,
                server_name,
                brand,
                model,
                serial_number,
                cpu,
                cpu_cores,
                ram,
                storage,
                storage_type,
                raid,
                operating_system,
                os_version,
                hostname,
                ip_address,
                mac_address,
                management_ip,
                data_center,
                rack,
                rack_position,
                assigned_to,
                condition,
                status,
                warranty,
                remarks

            FROM servers

            ORDER BY id DESC
        """)

        servers = cursor.fetchall()

    finally:

        conn.close()

    return render_template(
        "server_assets.html",
        servers=servers
    )
# =========================================================
# SERVER DETAILS
# =========================================================

@app.route("/server_details/<int:id>")
def server_details(id):

    conn = get_db_connection("Add_components.db")
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                id,
                product_id,
                server_name,
                brand,
                model,
                serial_number,

                cpu,
                cpu_cores,
                ram,
                storage,
                storage_type,
                raid,

                operating_system,
                os_version,

                hostname,
                ip_address,
                mac_address,
                management_ip,

                data_center,
                rack,
                rack_position,

                assigned_to,

                condition,
                status,

                warranty,
                remarks

            FROM servers

            WHERE id = ?

        """, (id,))

        server = cursor.fetchone()

    finally:

        conn.close()


    if not server:

        return "Server not found", 404


    return render_template(
        "server_details.html",
        server=server
    )



# =========================================================
# ADD USER
# =========================================================

@app.route(
    "/Add_user",
    methods=["GET", "POST"]
)
def Add_user():

    if request.method == "POST":

        employee_code = request.form.get(
            "Employee_code", ""
        ).strip()

        employee_name = request.form.get(
            "Employee_name", ""
        ).strip()

        tl_name = request.form.get(
            "TL_name", ""
        ).strip()

        team_name = request.form.get(
            "Team_name", ""
        ).strip()

        assigned_asset = request.form.get(
            "Assigned_asset", ""
        ).strip()

        location = request.form.get(
            "Location", ""
        ).strip()


        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        required_fields = {

            "Employee Code": employee_code,

            "Employee Name": employee_name,

            "TL Name": tl_name,

            "Team Name": team_name,

            "Location": location

        }


        missing_fields = [

            field
            for field, value in required_fields.items()
            if not value

        ]


        if missing_fields:

            return render_template(
                "User_details.html",
                error="Please fill all required fields.",
                missing_fields=missing_fields
            )


        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        conn = get_db_connection(
            "users.db"
        )

        cursor = conn.cursor()


        try:

            cursor.execute("""
                INSERT INTO users
                (
                    Employee_code,
                    Employee_name,
                    TL_name,
                    Team_name,
                    Assigned_asset,
                    Location
                )

                VALUES (?, ?, ?, ?, ?, ?)

            """, (

                employee_code,

                employee_name,

                tl_name,

                team_name,

                assigned_asset,

                location

            ))


            conn.commit()


        except sqlite3.Error as e:

            conn.rollback()

            return render_template(
                "User_details.html",
                error=f"Database Error: {e}"
            )


        finally:

            conn.close()


        return redirect(
            url_for("user_table")
        )


    return render_template(
        "User_details.html"
    )


# =========================================================
# DELETE USER
# =========================================================

@app.route("/delete_user/<int:id>")
def delete_user(id):

    conn = get_db_connection(
        "users.db"
    )

    cursor = conn.cursor()


    try:

        cursor.execute("""
            DELETE FROM users
            WHERE id = ?
        """, (id,))

        conn.commit()


    except sqlite3.Error as e:

        conn.rollback()

        return (
            f"Database Error: {e}",
            500
        )


    finally:

        conn.close()


    return redirect(
        url_for("user_table")
    )


# =========================================================
# EDIT USER
# =========================================================

@app.route("/edit_user/<int:id>")
def edit_user(id):

    conn = get_db_connection(
        "users.db"
    )

    cursor = conn.cursor()


    try:

        cursor.execute("""
            SELECT *
            FROM users
            WHERE id = ?
        """, (id,))

        user = cursor.fetchone()


    finally:

        conn.close()


    if user is None:

        return (
            "User not found.",
            404
        )


    return render_template(
        "User_details.html",
        user=user
    )


# =========================================================
# UPDATE USER
# =========================================================

@app.route(
    "/update_user/<int:id>",
    methods=["POST"]
)
def update_user(id):

    employee_code = request.form.get(
        "Employee_code", ""
    ).strip()

    employee_name = request.form.get(
        "Employee_name", ""
    ).strip()

    tl_name = request.form.get(
        "TL_name", ""
    ).strip()

    team_name = request.form.get(
        "Team_name", ""
    ).strip()

    assigned_asset = request.form.get(
        "Assigned_asset", ""
    ).strip()

    location = request.form.get(
        "Location", ""
    ).strip()


    conn = get_db_connection(
        "users.db"
    )

    cursor = conn.cursor()


    try:

        cursor.execute("""
            UPDATE users

            SET Employee_code = ?,
                Employee_name = ?,
                TL_name = ?,
                Team_name = ?,
                Assigned_asset = ?,
                Location = ?

            WHERE id = ?

        """, (

            employee_code,

            employee_name,

            tl_name,

            team_name,

            assigned_asset,

            location,

            id

        ))


        conn.commit()


    except sqlite3.Error as e:

        conn.rollback()

        return (
            f"Database Error: {e}",
            500
        )


    finally:

        conn.close()


    return redirect(
        url_for("user_table")
    )


# =========================================================
# USER TABLE
# =========================================================

@app.route("/user_table")
def user_table():

    conn = get_db_connection(
        "users.db"
    )

    cursor = conn.cursor()


    try:

        cursor.execute("""
            SELECT *
            FROM users
            ORDER BY id
        """)

        data = cursor.fetchall()


    finally:

        conn.close()


    return render_template(
        "user_table.html",
        data=data
    )


# =========================================================
# SCRAP DETAILS
# =========================================================

@app.route("/scrab_details")
def scrab_details():

    conn = get_db_connection(
        "Add_components.db"
    )

    cursor = conn.cursor()


    try:

        cursor.execute("""
            SELECT
                product_id,
                id,
                asset_category,
                brand,
                model,
                serial_number,
                seating_no,
                assigned_to,
                location,
                license,
                condition

            FROM assets

            WHERE LOWER(TRIM(condition))
                = 'damaged'

            ORDER BY id

        """)

        data = cursor.fetchall()


    finally:

        conn.close()


    return render_template(
        "scrab_details.html",
        data=data
    )


# =========================================================
# EXPORT EXCEL
# =========================================================

@app.route("/export_excel")
def export_excel():

    conn = get_db_connection(
        "Add_components.db"
    )

    cursor = conn.cursor()


    try:

        cursor.execute("""
            SELECT
                product_id,
                id,
                asset_category,
                brand,
                model,
                serial_number,
                seating_no,
                assigned_to,
                location,
                license,
                condition

            FROM assets

            ORDER BY id

        """)

        data = cursor.fetchall()


    finally:

        conn.close()


    # -----------------------------------------------------
    # CREATE EXCEL
    # -----------------------------------------------------

    wb = Workbook()

    ws = wb.active

    ws.title = "Assets"


    headers = [

        "Product ID",
        "ID",
        "Category",
        "Brand",
        "Model",
        "Serial No",
        "Seating No",
        "Assigned To",
        "Location",
        "License",
        "Condition"

    ]


    ws.append(headers)


    for row in data:

        ws.append(row)


    # -----------------------------------------------------
    # SAVE FILE
    # -----------------------------------------------------

    filename = "Assets_Report.xlsx"

    wb.save(filename)


    return send_file(
        filename,
        as_attachment=True
    )


# =========================================================
# ADD SERVER
# =========================================================

@app.route(
    "/add_server",
    methods=["GET", "POST"]
)
def add_server():

    if request.method == "GET":

        return render_template(
            "Add_server.html"
        )


    # -----------------------------------------------------
    # BASIC INFORMATION
    # -----------------------------------------------------

    product_id = request.form.get(
        "product_id", ""
    ).strip()

    server_name = request.form.get(
        "server_name", ""
    ).strip()

    brand = request.form.get(
        "brand", ""
    ).strip()

    model = request.form.get(
        "model", ""
    ).strip()

    serial_number = request.form.get(
        "serial_number", ""
    ).strip()


    # -----------------------------------------------------
    # HARDWARE
    # -----------------------------------------------------

    cpu = request.form.get(
        "cpu", ""
    ).strip()

    cpu_cores = request.form.get(
        "cpu_cores", ""
    ).strip()

    ram = request.form.get(
        "ram", ""
    ).strip()

    storage = request.form.get(
        "storage", ""
    ).strip()

    storage_type = request.form.get(
        "storage_type", ""
    ).strip()

    raid = request.form.get(
        "raid", ""
    ).strip() or None


    # -----------------------------------------------------
    # OPERATING SYSTEM
    # -----------------------------------------------------

    operating_system = request.form.get(
        "operating_system", ""
    ).strip()

    os_version = request.form.get(
        "os_version", ""
    ).strip() or None


    # -----------------------------------------------------
    # NETWORK
    # -----------------------------------------------------

    hostname = request.form.get(
        "hostname", ""
    ).strip()

    ip_address = request.form.get(
        "ip_address", ""
    ).strip()

    mac_address = request.form.get(
        "mac_address", ""
    ).strip()

    management_ip = request.form.get(
        "management_ip", ""
    ).strip() or None


    # -----------------------------------------------------
    # DATA CENTER
    # -----------------------------------------------------

    data_center = request.form.get(
        "data_center", ""
    ).strip()

    rack = request.form.get(
        "rack", ""
    ).strip()

    rack_position = request.form.get(
        "rack_position", ""
    ).strip() or None


    # -----------------------------------------------------
    # ASSIGNMENT
    # -----------------------------------------------------

    assigned_to = request.form.get(
        "assigned_to", ""
    ).strip() or None


    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    condition = request.form.get(
        "condition", ""
    ).strip()

    status = request.form.get(
        "status", ""
    ).strip()


    # -----------------------------------------------------
    # WARRANTY / REMARKS
    # -----------------------------------------------------

    warranty = request.form.get(
        "warranty", ""
    ).strip() or None

    remarks = request.form.get(
        "remarks", ""
    ).strip() or None


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    required_fields = {

        "Server Name": server_name,

        "Brand": brand,

        "Model": model,

        "Serial Number": serial_number,

        "CPU": cpu,

        "RAM": ram,

        "Storage": storage,

        "Operating System": operating_system,

        "Hostname": hostname,

        "IP Address": ip_address,

        "MAC Address": mac_address,

        "Data Center": data_center,

        "Rack": rack,

        "Condition": condition,

        "Status": status

    }


    missing_fields = [

        field
        for field, value in required_fields.items()
        if not value

    ]


    if missing_fields:

        return render_template(
            "Add_server.html",
            error="Please fill all required fields.",
            missing_fields=missing_fields
        )


    # -----------------------------------------------------
    # DATABASE
    # -----------------------------------------------------

    conn = get_db_connection(
        "Add_components.db"
    )

    cursor = conn.cursor()


    try:

        cursor.execute("""
            INSERT INTO servers
            (
                product_id,
                server_name,
                brand,
                model,
                serial_number,

                cpu,
                cpu_cores,
                ram,
                storage,
                storage_type,
                raid,

                operating_system,
                os_version,

                hostname,
                ip_address,
                mac_address,
                management_ip,

                data_center,
                rack,
                rack_position,

                assigned_to,

                condition,
                status,

                warranty,
                remarks
            )

            VALUES
            (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                ?,
                ?, ?,
                ?, ?
            )

        """, (

            product_id,

            server_name,

            brand,

            model,

            serial_number,

            cpu,

            cpu_cores,

            ram,

            storage,

            storage_type,

            raid,

            operating_system,

            os_version,

            hostname,

            ip_address,

            mac_address,

            management_ip,

            data_center,

            rack,

            rack_position,

            assigned_to,

            condition,

            status,

            warranty,

            remarks

        ))


        conn.commit()


    except sqlite3.Error as e:

        conn.rollback()

        return render_template(
            "Add_server.html",
            error=f"Database Error: {e}"
        )


    finally:

        conn.close()


    return render_template(
        "Add_server.html",
        success="Server added successfully."
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )