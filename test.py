import sqlite3

conn = sqlite3.connect("data.db")
cursor = conn.cursor()

create_table = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY , username text, password text)"
cursor.execute(create_table)

user = (1, "martin", "pass123")

insert_query = "INSERT INTO users VALUES (?, ?, ?)"
cursor.execute(insert_query, user)
conn.commit()

select_query = "SELECT * FROM users"
for row in cursor.execute(select_query):
    print(row)
conn.close()
