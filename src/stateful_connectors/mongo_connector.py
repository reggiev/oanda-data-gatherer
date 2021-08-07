import os
import pymongo

pymdb = os.environ.get('pymdb', "")


def get_client():
    pymuser = os.environ.get('pymuser', "")
    pympass = os.environ.get('pympass', "")
    url = os.environ.get('pymurl', "")

    creds = pymuser + ":" + pympass
    cl = pymongo.MongoClient("mongodb+srv://{}@{}/{}?ssl=true&ssl_cert_reqs=CERT_NONE".format(creds, url, pymdb))
    return cl


def count_docs(collection):
    cl = get_client()
    col = cl[pymdb][collection]
    c = col.count()

    cl.close()
    return c


def pymwriter(collection, data):
    cl = get_client()
    col = cl[pymdb][collection]

    upserts = [pymongo.UpdateOne({'_id': x['_id']}, {'$set': x}, upsert=True) for x in data]
    col.bulk_write(upserts)

    cl.close()
    pass


def pymreader(collection, params):
    pass


def find_docs(collection, params, limit=0, sort=None):
    cl = get_client()
    col = cl[pymdb][collection]

    if sort:
        res = col.find(params).sort(sort[0], sort[1]).limit(limit)
    else:
        res = col.find(params).limit(limit)

    cl.close()
    return res


def query_aggregate(collection, params):
    cl = get_client()
    col = cl[pymdb][collection]
    res = col.aggregate(params)

    cl.close()
    return res


def delete_documents(collection, query):
    cl = get_client()
    col = cl[pymdb][collection]
    e = col.remove(query)
    cl.close()
