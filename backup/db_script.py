import psycopg2

conn = psycopg2.connect("host=localhost dbname=postgres user=postgres")
cur = conn.cursor()
with open('College.csv','r') as f:
    next(f)
    cur.copy_from(f,'college', sep=',')

conn.commit()