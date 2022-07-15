import logging
import time
from http import HTTPStatus
from os import getenv
from pprint import pprint
from sys import getsizeof
from typing import Dict, List
import requests
assets = [
    'USDT',
    'BUSD',
    'BTC',
]
trade_types = [
    'BUY',
    'SELL'
]
fiats = [
    'RUB',
    'USD',
    'EUR',
]
pay_typeses = [
    'Tinkoff',
    'Wise',
#    'TBCbank',
#    'BankofGeorgia',
    'RosBank',
    'RUBfiatbalance',
]

ENDPOINT = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'


def create_data(asset, trade_type, fiat, pay_types):
    PAGE = 1
    ROWS = 1
    data = {
        "page": PAGE,
        "rows": ROWS,
        "publisherType": None,
        "asset": asset,
        "tradeType": trade_type,
        "fiat": fiat,
        "payTypes": [pay_types]
    }
    return data


def get_api_answer(data):
    """Делает запрос к единственному эндпоинту API.
    Яндекс.Практикума.
    """
    headers = {
        "Content-Type": "application/json",
        "Content-Length": str(getsizeof(data)),
    }
    try:
        response = requests.post(ENDPOINT, headers=headers, json=data)
    except Exception as error:
        message = f'Ошибка при запросе к основному API: {error}'
        raise Exception(message)
    if response.status_code != HTTPStatus.OK:
        message = f'Ошибка {response.status_code}'
        raise Exception(message)
    return response.json()


def parse_price(response):
    data = response.get('data')
    if len(data) == 0:
        price = None
        return price
    data1 = data[0]
    adv = data1.get('adv')
    price = adv.get('price')
    return price


# new_data = create_data(asset='USDT', trade_type='BUY', fiat='RUB', pay_types='Tinkoff')
# response = get_api_answer(new_data)
# price = parse_price(response)
# print(price)

def main():
    for asset in assets:
        for trade_type in trade_types:
            for fiat in fiats:
                for pay_types in pay_typeses:
                    if fiat == 'RUB' and pay_types == 'Wise':
                        continue
                    new_data = create_data(asset, trade_type,
                                           fiat, pay_types)
                    response = get_api_answer(new_data)
                    price = parse_price(response)
                    print(f'{asset}, {trade_type}, {fiat}, '
                          f'{pay_types}, {price}')


if __name__ == '__main__':
    main()
