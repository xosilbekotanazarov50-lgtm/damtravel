import sqlite3

DATABASE = "bot.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE orders ADD COLUMN lang TEXT DEFAULT 'ru'")
    conn.commit()
    print("Column 'lang' added successfully!")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("Column 'lang' already exists!")
    else:
        print(f"Error: {e}")
finally:
    conn.close()
