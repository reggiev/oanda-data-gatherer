import time
from datetime import datetime

from src.endpoints.pricing import get_instrument_pricing
from src.stateful_connectors.mongo_connector import pymwriter


def fetch_current_prices(ins, url, account_id):
    while True:
        _fetch_current_prices(ins, url, account_id)
        time.sleep(2)


def _fetch_current_prices(ins, url, account_id):
    res = get_instrument_pricing(url, account_id, json=None, params={"instruments": ins})
    prices = res["prices"]

    for i in range(0, len(prices)):
        # TODO Handle if the data model from Oanda suddenly changes
        prices[i]["_id"] = str(prices[i]["instrument"] + str(prices[i]["time"]))
        prices[i]["time"] = datetime.strptime(prices[i]["time"][:21], '%Y-%m-%dT%H:%M:%S.%f')
        prices[i]["closeoutBid"] = float(prices[i]["closeoutBid"])
        prices[i]["closeoutAsk"] = float(prices[i]["closeoutAsk"])
        prices[i]["tradeable"] = bool(prices[i]["tradeable"])
        prices[i]["quoteHomeConversionFactors"] = {
            "positiveUnits": float(prices[i]["quoteHomeConversionFactors"]["positiveUnits"]),
            "negativeUnits": float(prices[i]["quoteHomeConversionFactors"]["negativeUnits"])
        }
        prices[i]["unitsAvailable"]["default"]["long"] = int(float(prices[i]["unitsAvailable"]["default"]["long"]))
        prices[i]["unitsAvailable"]["default"]["short"] = int(float(prices[i]["unitsAvailable"]["default"]["short"]))
        prices[i]["unitsAvailable"]["openOnly"]["long"] = int(float(prices[i]["unitsAvailable"]["openOnly"]["long"]))
        prices[i]["unitsAvailable"]["openOnly"]["short"] = int(float(prices[i]["unitsAvailable"]["openOnly"]["short"]))
        prices[i]["unitsAvailable"]["reduceFirst"]["long"] = int(float(prices[i]["unitsAvailable"]["reduceFirst"]["long"]))
        prices[i]["unitsAvailable"]["reduceFirst"]["short"] = int(float(prices[i]["unitsAvailable"]["reduceFirst"]["short"]))
        prices[i]["unitsAvailable"]["reduceOnly"]["short"] = int(float(prices[i]["unitsAvailable"]["reduceOnly"]["short"]))
        prices[i]["unitsAvailable"]["reduceOnly"]["long"] = int(float(prices[i]["unitsAvailable"]["reduceOnly"]["long"]))
        prices[i]["bids"] = [{"price": float(q["price"]), "liquidity": int(q["liquidity"])} for q in prices[i]["bids"]]
        prices[i]["asks"] = [{"price": float(q["price"]), "liquidity": int(q["liquidity"])} for q in prices[i]["asks"]]
    pymwriter("price", prices)
