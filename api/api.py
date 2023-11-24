import json
from typing import Dict

from requests import Request, Session
from configs.config import configuration
import pprint

api_key_coin = configuration.API_KEY_COIN.get_secret_value()
api_key_crypto = configuration.API_KEY_CRYPTO.get_secret_value()


def api_coin(api_key: str):
    base_currency, target_currency = map(
        str, input("Введите основную и целевую валюты: ").split()
    )
    amount = int(input("Введите номинал: "))
    url = f"https://api.freecurrencyapi.com/v1/latest?apikey={api_key}&base_currency={base_currency}&currencies={target_currency}"

    response = Request("GET", url)

    info = response.json()

    if info["data"] and info["data"][target_currency]:
        converted = amount * info["data"][target_currency]
        print(f"{amount} {base_currency} составляют {converted} {target_currency}")
    else:
        print("Указанная валюта не найдена")


def api_crypto(parameters: Dict):
    # url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    # parameters = {
    #     "start": 1,
    #     "limit": 10,
    #     "convert": "USD"
    # }
    #
    # headers = {
    #     'Accepts': 'application/json',
    #     'X-CMC_PRO_API_KEY': api_key_crypto
    # }

    url = "https://pro-api.coinmarketcap.com/v2/tools/price-conversion"

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key_crypto
    }

    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)

    return json.loads(response.text)
