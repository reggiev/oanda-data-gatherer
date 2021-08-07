from datetime import datetime

from src.processes.system_event_writer import system_event
from src.stateful_connectors.mongo_connector import query_aggregate


def get_last_dates(collection, granularities):
    print("Getting the last update timestamp for all candles")
    dt = datetime.now()

    params = [
        {"$match": {"granularity": {"$in": granularities}}},
        {"$group": {"_id": {"$concat": ["$granularity", "$instrument"]}, "maxTime": {"$max": "$time"}}}]
    res = query_aggregate(collection, params)

    params = [
        {"$match": {"complete": False, "granularity": {"$in": granularities}}},
        {"$group": {"_id": {"$concat": ["$granularity", "$instrument"]}, "minTime": {"$min": "$time"}}}]
    res2 = query_aggregate(collection, params)

    dmax = {row["_id"]: row["maxTime"] for row in res}
    dmin = {row["_id"]: row["minTime"] for row in res2}

    # Determine the correct date to use
    for k in dmax.keys():
        if k not in dmin:
            dmin[k] = dmax[k]

    system_event("data_analyst", "get_last_dates", dt, remarks={"start": dt,
                                                                "end": datetime.now(),
                                                                "granularities": str(granularities),
                                                                "result": len(dmin)})
    return dmin
