import json
from typing import Dict

from requests import Request, Session
from configs.config import configuration
import pprint

api_key_coin = configuration.API_KEY_COIN.get_secret_value()
api_key_crypto = configuration.API_KEY_CRYPTO.get_secret_value()

headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': api_key_crypto
}


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


def api_crypto_exchange(parameters: Dict):
    url = "https://pro-api.coinmarketcap.com/v2/tools/price-conversion"

    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)

    return json.loads(response.text)


def api_crypto_info(crypto_symbol: str):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

    parameters = {
        "start": 1,
        "limit": 5000,
        "convert": "USD"
    }

    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)

    data = json.loads(response.text)["data"]

    target = dict()
    for coin in data:
        if coin["symbol"] == crypto_symbol:
            target = coin
            break

    info = {
        "Name": target["name"],
        "Symbol": target["symbol"],
        "Price": f'${round(target["quote"]["USD"]["price"], 5)} USD',
        "1hr Change": f'{round(target["quote"]["USD"]["percent_change_1h"], 2)}%',
        "24hr Change": f'{round(target["quote"]["USD"]["percent_change_24h"], 2)}%',
        "7d Change": f'{round(target["quote"]["USD"]["percent_change_7d"], 2)}%',
        "Volume": f'${round(target["quote"]["USD"]["price"] * target["total_supply"], 2)}',
        "Market Cap": f'${round(target["quote"]["USD"]["market_cap"], 2)}',
        "Circulating Supply": f'{round(target["circulating_supply"], 2)}',
        "Total Supply": f'{round(target["total_supply"], 2)}',
    }

    return info
