"""
Downloads the Chinook SQLite database (public domain demo dataset).
Run once: python setup_db.py
"""
import urllib.request
import os

DB_PATH = "data/chinook.db"
URL = "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"

os.makedirs("data", exist_ok=True)

if os.path.exists(DB_PATH):
    print(f"Database already exists at {DB_PATH}")
else:
    print("Downloading Chinook database...")
    urllib.request.urlretrieve(URL, DB_PATH)
    print(f"Saved to {DB_PATH}")

# Quick sanity check
import sqlite3
conn = sqlite3.connect(DB_PATH)
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print(f"\nTables found: {[t[0] for t in tables]}")
conn.close()
print("\nSetup complete. Run: uvicorn app.main:app --reload")
