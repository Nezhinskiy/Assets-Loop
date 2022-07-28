from http import HTTPStatus
from itertools import combinations
from typing import List

import requests

from binance.banks.models import FIATS

ENDPOINT = 'https://api.tinkoff.ru/v1/currency_rates?'


def generate_params() -> List[dict[str]]:
    fiats = [fiat[0] for fiat in FIATS]  # repackaging choices into a list
    fiats_combinations = tuple(combinations(fiats, 2))  # 2: currency pair
    params_list = [dict([('from', params[0]), ('to', params[-1])])
                   for params in fiats_combinations]
    # repackaging a list with tuples into a list with dicts
    return params_list


def get_api_answer(params):
    """Делает запрос к единственному эндпоинту API.
    Яндекс.Практикума.
    """
    try:
        response = requests.get(ENDPOINT, params)
    except Exception as error:
        message = f'Ошибка при запросе к основному API: {error}'
        raise Exception(message)
    if response.status_code != HTTPStatus.OK:
        message = f'Ошибка {response.status_code}'
        raise Exception(message)
    return response.json()


def parce_premium(response) -> dict:
    """Iterates through all dictionaries until 'Premium' is found."""
    payload = response['payload']
    rates = payload['rates']
    for category in rates:
        if category['category'] == 'CUTransfersPremium':
            return category


def parce_price(premium):
    price = premium.get('buy')
    return price


for params in generate_params():
    print(parce_price(get_api_answer(params)))

print(generate_params())
