from firebase import firebase
from multiprocessing import Pool
from psycopg2 import connect
from psycopg2.extensions import QuotedString
import requests

def postgres_escape(result, column):
    if column in ["type", "by", "url", "title", "text"]:
        return QuotedString(result[column]).getquoted().decode("utf-8", errors="ignore")
    if column in ["time"]:
        return "to_timestamp(%s)" % result[column]
    return str(result[column])

def main():
    fbase = firebase.FirebaseApplication('https://hacker-news.firebaseio.com/', None)

    con = connect(dbname='hackernews', user='postgres', host = 'localhost', password='Postgres1234')
    cur = con.cursor()

    def log_item(result):
        keys   = [key for key in result if key not in ["kids", "parts"]]
        values = [postgres_escape(result, key) for key in keys]
        cur.execute("INSERT INTO items (%s) VALUES (%s)" % (",".join(keys), ",".join(values)))
        con.commit()

    cur.execute("SELECT max(id) FROM items");
    res = cur.fetchall()
    max_id = res[0][0] if res[0][0] else 0
    print("Maximum Id: %d" % max_id)

    max_id_possible = fbase.get("/v0/maxitem", None)
    pool = Pool(50)

    items = range(max_id+1, max_id_possible+1)

    loc = 0

    while loc < len(items):
        try:
            batch = min(10000, len(items)-loc)
            for i in items[loc:loc+batch]:
                endpoint = fbase._build_endpoint_url("/v0/item/%d" % i, "")
                result = pool.apply_async(firebase.make_get_request, args=(endpoint, {}, {}), callback=log_item)
            result.get()
            print(items[loc+batch])
            loc += batch
        except requests.exceptions.HTTPError as exc:
            print(exc)
            print("Error on ", i)
            continue
        except KeyboardInterrupt:
            print("Caught KeyboardInterrupt, terminating workers")
            pool.terminate()
            pool.join()

    cur.close()
    con.close()

if __name__=="__main__":
    main()
