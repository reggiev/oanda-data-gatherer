from src.endpoints.general import process_request

def get_positions(instance, account_id):
    endpoint = "v3/accounts/{accountID}/positions".format(accountID=account_id)
    return process_request(method="get", url=instance+endpoint, json=None)

def get_open_positions(instance, account_id):
    endpoint = "v3/accounts/{accountID}/openPositions".format(accountID=account_id)
    return process_request(method="get", url=instance+endpoint, json=None)

def get_open_instrument_position(instance, account_id, instrument):
    endpoint = "v3/accounts/{accountID}/positions/{instrument}".format(accountID=account_id, instrument=instrument)
    return process_request(method="get", url=instance+endpoint, json=None)

#TODO Study what is meant by closed instrument
def close_open_instrument_position(instance, account_id, instrument):
    endpoint = "v3/accounts/{accountID}/positions/{instrument}/close".format(accountID=account_id, instrument=instrument)
    return process_request(method="get", url=instance+endpoint, json=None)