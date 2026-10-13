"""
setup_database.py

This python script is for setting up a SQLite database for 
the flight management system. It creates the database file,
defines the schema, and populates it with sample data.

Usage:
    python setup_database.py <name_of_db.db>   
"""

import sqlite3
import sys
from pathlib import Path

default_db = "flight_management.db"
schema_file =  "schema.sql"
sample_data_file = "sample_data.sql"

def build_database(db_path=default_db):

    db_path = Path(db_path)
    if db_path.exists():
        print(f"Database already exists at: {db_path}")
        print('Do you want to overwrite it? (y/n): ', end='')
        choice = input()
        if choice.lower() != 'y':
            print("Operation cancelled.")   
            return
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(Path(schema_file).read_text(encoding="utf-8"))
        conn.executescript(Path(sample_data_file).read_text(encoding="utf-8"))
        conn.commit()

        print(f"Database created at: {db_path}")

    finally:
        conn.close()

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else default_db
    build_database(target)
