from src.endpoints.general import process_request

def get_transactions(instance, account_id, params):
    endpoint = "v3/accounts/{accountID}/transactions".format(accountID=account_id)
    return process_request(method="get", url=instance+endpoint, json=params)

def get_transaction_info(instance, account_id, transaction_id, params):
    endpoint = "v3/accounts/{accountID}/transactions/{transactionID}".format(accountID=account_id, transactionID=transaction_id)
    return process_request(method="get", url=instance+endpoint, json=params)

def get_transaction_list_from_id(instance, account_id, json, params):
    endpoint = "v3/accounts/{accountID}/transactions/sinceid".format(accountID=account_id)
    return process_request(method="get", url=instance+endpoint, json=None, params=params)

def get_transaction_list_from_range(instance, account_id, json, params):
    endpoint = "v3/accounts/{accountID}/transactions/idrange".format(accountID=account_id)
    return process_request(method="get", url=instance+endpoint, json=None, params=params)

# TODO implement a more sensible transaction stream feature
def open_transactions_stream(instance, account_id, transaction_id, params):
    endpoint = "v3/accounts/{accountID}/transactions/stream".format(accountID=account_id)
    return process_request(method="get", url=instance+endpoint, json=params)

# with requests.get(url, stream=True) as r:
#     r.raise_for_status()
#     with open(local_filename, 'wb') as f:
#         for chunk in r.iter_content(chunk_size=8192): 
#             # If you have chunk encoded response uncomment if
#             # and set chunk_size parameter to None.
#             #if chunk: 
#             f.write(chunk)