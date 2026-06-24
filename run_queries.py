import sqlite3

conn = sqlite3.connect('data/db/bluestock_mf.db')
cursor = conn.cursor()

# Read file with utf-8-sig to remove BOM
with open('sql/queries.sql', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Split by semicolon but ignore those inside comments (simple approach)
queries = [q.strip() for q in content.split(';') if q.strip()]

for q in queries:
    try:
        result = cursor.execute(q).fetchall()
        if result:
            print(result)
        else:
            print("Query executed (no rows returned)")
    except Exception as e:
        print(f"Error in query:\n{q}\nError: {e}")

conn.close()