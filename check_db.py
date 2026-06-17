import sqlite3

con = sqlite3.connect('hn_stories.db')
rows = con.execute("SELECT id, title, summary, fetched_at FROM story ORDER BY fetched_at DESC LIMIT 20").fetchall()
for row in rows:
    status = "OK" if row[2] else "MISSING"
    print(f"{status} | {row[0]} | {row[1][:40]}")