import pyodbc
conn_str = r'Driver={SQLite3 ODBC Driver};Database=C:\Users\dell\OneDrive\Desktop\bluestock_mf_capstone\data\db\bluestock_mf.db;'
conn = pyodbc.connect(conn_str)
print("Connected!")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())