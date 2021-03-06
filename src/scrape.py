from firebase import firebase
from multiprocessing import Pool
from psycopg2 import connect
from psycopg2.extensions import QuotedString
import requests
import time

def postgres_escape(result, column):
    if column in ["type", "by", "url", "title", "text"]:
        try:
            return QuotedString(result[column].encode("ascii", errors="ignore").decode("ascii", errors="ignore")).getquoted().decode("ascii", errors="ignore")
        except:
            f = open("error.csv", "w")
            f.write(result[column])
            f.close()
            f = open("error2.csv", "w")
            f.write(QuotedString(result[column]).getquoted())
            f.close()
            raise
    if column in ["time"]:
        return "to_timestamp(%s)" % result[column]
    if column in ["deleted"] and result[column]=="yes":
        return "TRUE"
    return str(result[column])

def main():
    fbase = firebase.FirebaseApplication('https://hacker-news.firebaseio.com/', None)

    con = connect(dbname='hackernews', user='postgres', host = 'localhost', password='Postgres1234')
    cur = con.cursor()

    def log_item(result):
        if result is None:
            print("Response was empty ... continuing")
            return
        keys   = [key for key in result if key not in ["kids", "parts"]]
        values = [postgres_escape(result, key) for key in keys]
        try:
            cur.execute("INSERT INTO items (%s) VALUES (%s)" % (",".join(keys), ",".join(values)))
        except:
            f = open("sqlerror.csv", "w")
            f.write("INSERT INTO items (%s) VALUES (%s)" % (",".join(keys), ",".join(values)))
            f.close()
            raise
        if "kids" in result:
            for i in range(0, len(result["kids"])):
                cur.execute("INSERT INTO item_kid (item_id, kid_id, display_rank) VALUES (%d,%d,%d)" % (result["id"], result["kids"][i], i+1))
        if "parts" in result:
            for i in range(0, len(result["parts"])):
                cur.execute("INSERT INTO item_part (item_id, part_id, display_rank) VALUES (%d,%d,%d)" % (result["id"], result["parts"][i], i+1))
        con.commit()

    cur.execute("SELECT max(id) FROM items");
    res = cur.fetchall()
    max_id = res[0][0] if res[0][0] else 0
    print("Maximum Id Scraped: %d" % max_id)

    max_id_possible = fbase.get("/v0/maxitem", None)
    print("Maximum Id On Firebase: %d" % max_id_possible)
    pool = Pool(5)

    items = range(max_id+1, max_id_possible+1)

    loc = 0

    while loc < len(items)-1:
        try:
            start = time.time()
            batch = min(10000, len(items)-loc-1)
            for i in items[loc:loc+batch]:
                endpoint = fbase._build_endpoint_url("/v0/item/%d" % i, "")
                result = pool.apply_async(firebase.make_get_request, args=(endpoint, {}, {}), callback=log_item)
            result.get(0xFFFF) # specifying a timeout to get the keyboard interrupt
            print("Item: %d, Elapsed Time: %0.2f, Items/Second: %0.2f" % (items[loc+batch], time.time()-start, batch/(time.time()-start)))
            loc += batch
        except requests.exceptions.HTTPError as exc:
            print(exc)
            print("Error on ", i)
            continue
        except KeyboardInterrupt:
            print("Caught KeyboardInterrupt, terminating workers")
            pool.terminate()
            pool.join()

    pool.terminate()
    pool.join()
    
    cur.close()
    con.close()

if __name__=="__main__":
    main()
