# ==============================================================================
# DATABASE CONFIGURATION & CONNECTION (MySQL with Auto-Fallback)
# ==============================================================================
# This file handles connecting to MySQL and creating the database/table.
# It is designed to be simple, reliable, and easy to explain in a college viva.
# If MySQL credentials are not yet configured or MySQL service is stopped,
# it automatically provides a seamless local database fallback so the app works!
# ==============================================================================

import os
import sqlite3
import mysql.connector
from mysql.connector import Error

# ------------------------------------------------------------------------------
# 1. DATABASE CREDENTIALS (MySQL)
# Change these values according to your MySQL installation (e.g. XAMPP or MySQL Workbench)
# ------------------------------------------------------------------------------
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""      # <-- Enter your MySQL password here (e.g. "root", "admin", or "")
DB_NAME = "contact_book"

# Tracking active database engine
ACTIVE_DB_ENGINE = "MySQL"


# ------------------------------------------------------------------------------
# 2. SQLITE FALLBACK WRAPPERS
# Ensures identical dictionary cursor behavior and %s placeholder compatibility
# ------------------------------------------------------------------------------
class SQLiteCursorWrapper:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, params=None):
        # Convert MySQL %s placeholder to SQLite ? placeholder
        query = query.replace("%s", "?")
        if params is not None:
            return self._cursor.execute(query, params)
        return self._cursor.execute(query)

    def executemany(self, query, seq_of_params):
        query = query.replace("%s", "?")
        return self._cursor.executemany(query, seq_of_params)

    def fetchone(self):
        row = self._cursor.fetchone()
        return dict(row) if row else None

    def fetchall(self):
        rows = self._cursor.fetchall()
        return [dict(r) for r in rows]

    def close(self):
        self._cursor.close()


class SQLiteConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn
        self._conn.row_factory = sqlite3.Row

    def cursor(self, dictionary=True):
        return SQLiteCursorWrapper(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def get_db_connection():
    """
    Connects to MySQL database.
    If MySQL connection fails (e.g. password required), safely falls back
    to local SQLite database so the application works seamlessly.
    """
    global ACTIVE_DB_ENGINE
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        ACTIVE_DB_ENGINE = "MySQL"
        return connection
    except Error:
        # Fallback to local SQLite database
        ACTIVE_DB_ENGINE = "SQLite (Fallback)"
        db_path = os.path.join(os.path.dirname(__file__), "contact_book.db")
        conn = sqlite3.connect(db_path)
        return SQLiteConnectionWrapper(conn)


def init_database():
    """
    Initializes the database:
    1. Tries MySQL first: creates database & table.
    2. If MySQL fails, initializes local SQLite database.
    3. Adds sample starter contacts if empty.
    """
    global ACTIVE_DB_ENGINE
    mysql_success = False

    # Attempt MySQL initialization
    try:
        server_conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = server_conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.close()
        server_conn.close()

        db_conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = db_conn.cursor()
        # 2. Contacts Table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS contacts (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            email VARCHAR(100),
            address VARCHAR(255),
            group_name VARCHAR(50),
            favorite BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)

        # 3. Users Table for Authentication
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_users_table)
        db_conn.commit()

        # Seed default admin user if not present
        from werkzeug.security import generate_password_hash
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", ("admin",))
        if cursor.fetchone()[0] == 0:
            default_pwd_hash = generate_password_hash("admin123")
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                ("admin", default_pwd_hash)
            )
            db_conn.commit()

        # Seed sample data if empty
        cursor.execute("SELECT COUNT(*) AS total FROM contacts")
        count = cursor.fetchone()[0]
        if count == 0:
            sample_contacts = [
                ("Rahul Sharma", "9876543210", "rahul@gmail.com", "Agra, Uttar Pradesh", "College", True),
                ("Priya Patel", "9123456780", "priya@gmail.com", "Ahmedabad, Gujarat", "Friends", True),
                ("Amit Verma", "9988776655", "amit.verma@example.com", "New Delhi, Delhi", "Work", False),
                ("Neha Gupta", "9456123789", "neha@yahoo.com", "Jaipur, Rajasthan", "Family", False)
            ]
            insert_query = """
            INSERT INTO contacts (name, phone, email, address, group_name, favorite)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_query, sample_contacts)
            db_conn.commit()

        cursor.close()
        db_conn.close()
        ACTIVE_DB_ENGINE = "MySQL"
        print("[SUCCESS] MySQL Database & Tables initialized successfully.")
        return True

    except Error as e:
        print(f"[NOTE] MySQL not ready ({e}). Initializing local fallback database...")

    # Fallback to local SQLite initialization
    try:
        from werkzeug.security import generate_password_hash
        db_path = os.path.join(os.path.dirname(__file__), "contact_book.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            address TEXT,
            group_name TEXT,
            favorite INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()

        # Seed default admin user in SQLite
        cur.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("admin",))
        if cur.fetchone()[0] == 0:
            default_pwd_hash = generate_password_hash("admin123")
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                ("admin", default_pwd_hash)
            )
            conn.commit()

        cur.execute("SELECT COUNT(*) FROM contacts")
        count = cur.fetchone()[0]
        if count == 0:
            sample_contacts = [
                ("Rahul Sharma", "9876543210", "rahul@gmail.com", "Agra, Uttar Pradesh", "College", 1),
                ("Priya Patel", "9123456780", "priya@gmail.com", "Ahmedabad, Gujarat", "Friends", 1),
                ("Amit Verma", "9988776655", "amit.verma@example.com", "New Delhi, Delhi", "Work", 0),
                ("Neha Gupta", "9456123789", "neha@yahoo.com", "Jaipur, Rajasthan", "Family", 0)
            ]
            cur.executemany("""
            INSERT INTO contacts (name, phone, email, address, group_name, favorite)
            VALUES (?, ?, ?, ?, ?, ?)
            """, sample_contacts)
            conn.commit()

        cur.close()
        conn.close()
        ACTIVE_DB_ENGINE = "SQLite (Fallback)"
        print("[SUCCESS] Local Database initialized successfully with sample starter contacts.")
        return True

    except Exception as ex:
        print(f"[ERROR] Database initialization failed: {ex}")
        return False


if __name__ == "__main__":
    print("Testing Database Connection and Initialization...")
    init_database()
