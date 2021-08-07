from src.platforms.oanda.general import process_request


def get_accounts(instance):
    endpoint = "v3/accounts"
    return process_request(method="get", url=instance+endpoint, json=None)


def get_account_info(instance, account_id):
    endpoint = "v3/accounts/{accountID}".format(accountID=account_id)
    return process_request(method="get", url=instance+endpoint, json=None)


def get_instruments(instance, account_id):
    endpoint = "v3/accounts/{accountID}/instruments".format(
        accountID=account_id)
    return process_request(method="get", url=instance+endpoint, json=None).get("instruments")
