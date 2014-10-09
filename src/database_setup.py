from psycopg2 import connect
import sys
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

con = connect(dbname='postgres', user='postgres', host = 'localhost', password='Postgres1234')

con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = con.cursor()
cur.execute("SELECT 1 from pg_database WHERE datname='hackernews';")
rows = cur.fetchall()
if rows:
	cur.execute('DROP DATABASE hackernews;')
cur.execute('CREATE DATABASE hackernews;')
cur.close()
con.close()

with open('model.sql', 'r') as f:
	model = f.read()

con = connect(dbname='hackernews', user='postgres', host = 'localhost', password='Postgres1234')
cur = con.cursor()
cur.execute(model)
con.commit()
cur.close()
con.close()
