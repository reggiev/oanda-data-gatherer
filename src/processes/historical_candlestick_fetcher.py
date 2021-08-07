import time
import urllib
from datetime import datetime, timedelta

import schedule

from src.endpoints.pricing import get_instrument_candlestick
from src.processes.last_dates_fetcher import get_last_dates
from src.processes.system_event_writer import system_event
from src.stateful_connectors.mongo_connector import pymwriter

g_priority = {
    "M": 9,
    "D": 8,
    "H12": 7,
    "H1": 5,
    "M5": 4,
    "S5": 3
}


def fetch_historical_candlestick(inl, interval, url, account_id):
    if interval[0] == "M5":
        # 4 days worth of 5 minute denominated candles
        dimension = {"M5": 1140}
        schedule.every(5).minutes.at(":05").do(
            lambda: _fetch_historical_candlestick(dimension, inl, url, account_id))
    elif interval[0] == "H1":
        dimension = {"H1": 480}  # 20 days worth of 1 hour denominated candles
        schedule.every(60).minutes.at(":35").do(
            lambda: _fetch_historical_candlestick(dimension, inl, url, account_id))
    elif interval[0] == "H12":
        # 4 months worth of 12 hour denominated candles
        dimension = {"H12": 244}
        schedule.every(720).minutes.at(":30").do(
            lambda: _fetch_historical_candlestick(dimension, inl, url, account_id))
    elif interval[0] == "D":
        # 4 years worth of 1 day denominated candles
        # 10 years worth of 1 month denominated candles
        dimension = {"D": 1460, "M": 120}
        schedule.every(12).hours.at(":15").do(
            lambda: _fetch_historical_candlestick(dimension, inl, url, account_id))

    while True:
        schedule.run_pending()
        time.sleep(1)  # Sleep for 1 second


def _fetch_historical_candlestick(dimension, inl, url, account_id):
    dt = datetime.now()

    dimen_name = str(dimension).replace("{", "").replace(
        " ", "").replace("_", "").replace("}", "").replace("'", "")
    event_name = "_fetch_historical_candlestick_" + \
        dimen_name.replace(",", "_").replace(":", "_")

    price = "ABM"
    data = []

    # Query for the last candle dates in stateful
    last_candle_dates = get_last_dates("candle", list(dimension.keys()))

    for granularity in dimension.keys():
        for inst in inl:
            params = {
                "price": price,
                "granularity": granularity,
                "count": dimension[granularity]
            }

            # Check if a certain instrument and granularity has last saved date
            if (granularity + inst) in last_candle_dates:
                # Stored time is in UTC but time used to talk to server is in UTC-4
                # Sometimes daylight savings may affect this
                params["from"] = str(
                    last_candle_dates[(granularity + inst)] - timedelta(hours=5))
                params = urllib.parse.urlencode(
                    params, quote_via=urllib.parse.quote)

            tmp = get_instrument_candlestick(
                url, account_id, inst, None, params)

            if "candles" not in tmp:
                print("Candles not found in tmp. Check response")
                print(tmp)
                continue

            for row in tmp["candles"]:
                cleaned_time = row["time"][:21].replace(":", "").replace("-", "").replace(".", "") + \
                    tmp["instrument"].replace("_", "")
                cid = str(g_priority[tmp["granularity"]]) + \
                    cleaned_time + tmp["granularity"]
                cid = cid + ("0" * (27 - len(cid)))
                ctime = datetime.strptime(
                    row["time"][:21], '%Y-%m-%dT%H:%M:%S.%f')

                data.append({
                    "instrument": tmp["instrument"],
                    "granularity": tmp["granularity"],
                    "time": ctime,
                    "_id": cid,
                    "complete": bool(row["complete"]),
                    "bid": {
                        "o": float(row["bid"]["o"]),
                        "c": float(row["bid"]["c"]),
                        "h": float(row["bid"]["h"]),
                        "i": float(row["bid"]["l"]),
                    },
                    "ask": {
                        "o": float(row["ask"]["o"]),
                        "c": float(row["ask"]["c"]),
                        "h": float(row["ask"]["h"]),
                        "i": float(row["ask"]["l"]),
                    },
                    "mid": {
                        "o": float(row["mid"]["o"]),
                        "c": float(row["mid"]["c"]),
                        "h": float(row["mid"]["h"]),
                        "i": float(row["mid"]["l"]),
                    }
                })

            if len(data) >= 200:
                pymwriter("candle", data)
                data = []

    system_event("data_analyst", event_name, dt, remarks={
                 "start": dt, "end": datetime.now()})
    print("Done fetching instrument candles.")
