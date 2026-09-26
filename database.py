import sqlite3
from pathlib import Path


# Project root folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Database location
DATABASE = BASE_DIR / "database" / "agroguard.db"


def get_connection():
    return sqlite3.connect(str(DATABASE))


def create_tables():

    # Make sure database folder exists
    DATABASE.parent.mkdir(parents=True, exist_ok=True)

    connection = get_connection()
    cursor = connection.cursor()

    # Farmers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            crop TEXT
        )
    """)

    # Scan history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER NOT NULL,
            crop TEXT,
            disease TEXT,
            confidence REAL,
            severity TEXT,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (farmer_id) REFERENCES farmers(id)
        )
    """)

    connection.commit()
    connection.close()

    print("✅ AgroGuard AI database created successfully!")
    print(f"📁 Database: {DATABASE}")


if __name__ == "__main__":
    create_tables()
