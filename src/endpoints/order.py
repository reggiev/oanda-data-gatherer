from src.endpoints.general import process_request

def get_order_list(instance, account_id, params):
    endpoint = "v3/accounts/{accountID}/orders".format(accountID=account_id)
    return process_request(method="get", url=instance+endpoint, json=params)

def get_pending_order_list(instance, account_id, params):
    endpoint = "v3/accounts/{accountID}/pendingOrders".format(accountID=account_id)
    return process_request(method="get", url=instance+endpoint, json=params)

def create_order(instance, account_id, params):
    endpoint = "v3/accounts/{accountID}/orders".format(accountID=account_id)
    return process_request(method="post", url=instance+endpoint, json=params)

#TODO Test this
def get_order_info(instance, account_id, order_specifier):
    endpoint = "v3/accounts/{accountID}/orders/{orderSpecifier}".format(accountID=account_id, orderSpecifier=order_specifier)
    return process_request(method="get", url=instance+endpoint, json=None)

#TODO Replace order
def replace_order(instance, account_id, order_specifier, params):
    endpoint = "v3/accounts/{accountID}/orders/{orderSpecifier}".format(accountID=account_id, orderSpecifier=order_specifier)
    return process_request(method="put", url=instance+endpoint, json=params)

#TODO Cancel order
def cancel_order(instance, account_id, order_specifier, params):
    endpoint = "v3/accounts/{accountID}/orders/{orderSpecifier}/cancel".format(accountID=account_id, orderSpecifier=order_specifier)
    return process_request(method="put", url=instance+endpoint, json=params)
