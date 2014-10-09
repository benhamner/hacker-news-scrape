from firebase import firebase
from psycopg2 import connect
from psycopg2.extensions import QuotedString
import requests

def escape(result, key):
    if key in ["type", "by", "url", "title", "text"]:
        return QuotedString(result[key]).getquoted().decode("utf-8", errors="replace")
    if key in ["time"]:
        return "to_timestamp(%s)" % result[key]
    return str(result[key])

def main():
    fbase = firebase.FirebaseApplication('https://hacker-news.firebaseio.com/', None)

    con = connect(dbname='hackernews', user='postgres', host = 'localhost', password='Postgres1234')
    cur = con.cursor()

    def log_item(result):
        keys   = [key for key in result if key not in ["kids", "parts"]]
        values = [escape(result, key) for key in keys]
        cur.execute("INSERT INTO items (%s) VALUES (%s)" % (",".join(keys), ",".join(values)))
        con.commit()

    cur.execute("SELECT max(id) FROM items");
    res = cur.fetchall()
    max_id = res[0][0] if res[0][0] else 0
    print("Maximum Id: %d" % max_id)

    max_id_possible = fbase.get("/v0/maxitem", None)

    for i in range(max_id+1, max_id_possible+1):
        try:
            result = fbase.get_async("/v0/item/%d" % i, None, callback=log_item)
            if i%100==0:
                print(i)
                result.get()
        except requests.exceptions.HTTPError as exc:
            print(exc)
            print("Error on ", i)
            continue

    cur.close()
    con.close()

if __name__=="__main__":
    main()
