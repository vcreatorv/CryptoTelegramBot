import json
from typing import Dict

from requests import Session
from configs.config import configuration

api_key_coin = configuration.API_KEY_COIN.get_secret_value()
api_key_crypto = configuration.API_KEY_CRYPTO.get_secret_value()


def api_crypto(parameters: Dict):
    url = "https://pro-api.coinmarketcap.com/v2/tools/price-conversion"

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key_crypto
    }

    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)

    return json.loads(response.text)
