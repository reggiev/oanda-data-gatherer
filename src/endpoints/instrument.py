from src.platforms.oanda.general import process_request

def get_candlesticks(instance, instrument, params):
    endpoint = "v3/instruments/{instrument}/candles".format(instrument=instrument)
    return process_request(method="get", url=instance+endpoint, json=params)

def get_orderbook(instance, instrument, params):
    endpoint = "v3/instruments/{instrument}/orderBook".format(instrument=instrument)
    return process_request(method="get", url=instance+endpoint, json=params)

def get_positionbook(instance, instrument, params):
    endpoint = "v3/instruments/{instrument}/positionBook".format(instrument=instrument)
    return process_request(method="get", url=instance+endpoint, json=params)