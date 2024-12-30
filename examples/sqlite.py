import sqlite3

# Test SQLite interaction
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT);")
conn.commit()
print("SQLite is working; table created.")
conn.close()
