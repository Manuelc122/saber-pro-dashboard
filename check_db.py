import sqlite3
from pathlib import Path

# Get the absolute path to the database
db_path = Path(__file__).parent / 'data' / 'processed' / 'saber_pro.db'

print(f"Looking for database at: {db_path}")
print(f"Database exists: {db_path.exists()}")

if db_path.exists():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("\nTables in database:", tables)
    
    # Check row count
    cursor.execute("SELECT COUNT(*) FROM saber_pro;")
    count = cursor.fetchone()[0]
    print("Number of rows:", count)
    
    conn.close() 