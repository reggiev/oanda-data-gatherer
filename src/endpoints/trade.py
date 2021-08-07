from src.platforms.oanda.general import process_request

def get_trades(instance, account_id, params):
    endpoint = "v3/accounts/{accountID}/trades".format(accountID=account_id)
    return process_request(method="get", url=instance+endpoint, json=params)

def get_open_trades(instance, account_id):
    endpoint = "v3/accounts/{accountID}/openTrades".format(accountID=account_id)
    return process_request(method="get", url=instance+endpoint, json=None)

def get_trade_info(instance, account_id, trade_specifier):
    endpoint = "v3/accounts/{accountID}/trades/{tradeSpecifier}".format(accountID=account_id, tradeSpecifier=trade_specifier)
    return process_request(method="get", url=instance+endpoint, json=None)

def close_trade(instance, account_id, trade_specifier, json, params):
    endpoint = "v3/accounts/{accountID}/trades/{tradeSpecifier}/close".format(accountID=account_id, tradeSpecifier=trade_specifier)
    return process_request(method="put", url=instance+endpoint, json=None, params=params)

#TODO Study the clientExtensions
#PUT	/v3/accounts/{accountID}/trades/{tradeSpecifier}/clientExtensions
#Update the Client Extensions for a Trade. Do not add, update, or delete the Client Extensions if your account is associated with MT4.

#TODO Study this endpoint
#PUT	/v3/accounts/{accountID}/trades/{tradeSpecifier}/orders
#Create, replace and cancel a Trade’s dependent Orders (Take Profit, Stop Loss and Trailing Stop Loss) through the Trade itself
