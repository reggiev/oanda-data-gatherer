from src.platforms.oanda.general import process_request


def get_latest_candles(instance, account_id, json, params):
    endpoint = "v3/accounts/{accountID}/candles/latest".format(
        accountID=account_id)
    return process_request(method="get", url=instance+endpoint, json=json, params=params)


def get_instrument_pricing(instance, account_id, json, params):
    endpoint = "v3/accounts/{accountID}/pricing".format(accountID=account_id)
    return process_request(method="get", url=instance+endpoint, json=None, params=params)


def get_instrument_candlestick(instance, account_id, instrument, json, params):
    endpoint = "v3/accounts/{accountID}/instruments/{instrument}/candles".format(
        accountID=account_id, instrument=instrument)
    return process_request(method="get", url=instance+endpoint, json=json, params=params)
