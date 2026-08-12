import sqlite3
from pathlib import Path

DB_PATH = Path("books.db")

if not DB_PATH.exists():
    print("ERROR: books.db not found!")
else:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
    """)

    tables = cursor.fetchall()

    print("Tables in old SQLite database:\n")

    for (table,) in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} records")

    conn.close()