import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / 'db.sqlite3'

con = sqlite3.connect(str(DB_PATH))
try:
    cur = con.cursor()
    cur.execute("DELETE FROM django_migrations WHERE app=? AND name=?", ('hr', '0003_delete_acte'))
    con.commit()
    print('Deleted rows:', cur.rowcount)
finally:
    con.close()


