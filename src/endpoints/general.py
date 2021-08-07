import json
import os, rsa, base64
from datetime import datetime

import requests


def fetch_token():
    key = os.environ.get('oanda_key', "")
    return key


def process_request(method, url, json, params=None):
    headers = {
        "Authorization": "Bearer " + fetch_token()
    }

    req = requests.Request(method=method, url=url,
                           headers=headers, json=json, params=params)
    prepared = req.prepare()
    # pretty_print_POST(prepared)
    s = requests.Session()
    res = s.send(prepared)
    res.raise_for_status()
    return res.json()


def encrypt(data):
    """
        item: string to be encrypted
        pub_key: pem key to use for encryption
    """
    n = 100
    delimeter = "#"
    pub_key = rsa.PublicKey._load_pkcs1_pem(os.environ.get('pub_key', ""))
    data = str(data)

    # slice the item so that it will fit to the encryption
    chunks = [data[i:i+n] for i in range(0, len(data), n)]
    return delimeter.join(base64.b64encode(rsa.encrypt(chunk.encode(), pub_key)).decode('UTF-8') for chunk in chunks)


def decrypt(data):
    """
        item: string to be encrypted
        pub_key: pem key to use for encryption
    """
    delimeter = "#"
    priv_key = rsa.PrivateKey._load_pkcs1_pem(os.environ.get('priv_key', ""))

    encrypted_chunks = data.split(delimeter)
    return "".join(rsa.decrypt(base64.b64decode(c.encode('UTF-8')), priv_key).decode() for c in encrypted_chunks)


def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))


def is_market_hours():
    day_name = datetime.now().strftime("%A")
    hour = int(datetime.now().strftime("%H"))

    if day_name == "Saturday":
        return False
    elif day_name == "Friday":
        if hour >= 21:
            return False
    elif day_name == "Sunday":
        if hour < 21:
            return False
    return True
