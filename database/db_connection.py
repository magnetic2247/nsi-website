import sqlite3

# Connection
conn = sqlite3.connect("database/db.sqlite")
conn.row_factory = sqlite3.Row

# Query with error-handling
def query(sql, bindings=()):
    global conn
    try:
        cursor = conn.execute(sql, bindings)
        conn.commit()
    except sqlite3.Error as err:
        print("SQL Error:", err)
        return
    return cursor


