import time
from http import HTTPStatus
from sys import getsizeof

import requests

from parses_p2p.models import ASSETS, FIATS, PAY_TYPES, TRADE_TYPES, UpdateP2P
# import os
# # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'binance.binance.settings')
# from binance_api.parses_p2p.models import UpdateP2P
# from binance_api.binance_api.settings import BASE_DIR

ENDPOINT = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
PAGE = 1
ROWS = 1


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
    start_time = time.perf_counter_ns()
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
    duration = start_time - time.perf_counter_ns()
    UpdateP2P.objects.create(duration=duration)


if __name__ == '__main__':
    main()
