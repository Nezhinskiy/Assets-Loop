import logging
import time
from http import HTTPStatus
from os import getenv
from pprint import pprint
from sys import getsizeof
from typing import Dict, List

import requests

from binance.parses_p2p.parameters import (ASSETS, ENDPOINT, FIATS, PAGE,
                                           PAY_TYPES, ROWS, TRADE_TYPES)


def create_data(asset, trade_type, fiat, pay_types):
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


def main():
    for asset in ASSETS:
        asset = asset[0]
        for trade_type in TRADE_TYPES:
            trade_type = trade_type[0]
            for fiat in FIATS:
                fiat = fiat[0]
                for pay_type in PAY_TYPES:
                    pay_type = pay_type[0]
                    if fiat == 'RUB' and pay_type == 'Wise':
                        continue
                    new_data = create_data(asset, trade_type,
                                           fiat, pay_type)
                    response = get_api_answer(new_data)
                    price = parse_price(response)
                    print(f'{asset}, {trade_type}, {fiat}, '
                          f'{pay_type}, {price}')


if __name__ == '__main__':
    main()
