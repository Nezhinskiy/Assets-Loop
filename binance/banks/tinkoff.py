from http import HTTPStatus
from itertools import combinations
from typing import List

import requests

from binance.banks.models import FIATS

ENDPOINT = 'https://api.tinkoff.ru/v1/currency_rates?'


def generate_params() -> List[dict[str]]:
    fiats = [fiat[0] for fiat in FIATS]
    fiats_combinations = tuple(combinations(fiats, 2))
    params_list = [dict([('from', params[0]), ('to', params[-1])])
                   for params in fiats_combinations]
    return params_list


def get_api_answer(params_list):
    """Делает запрос к единственному эндпоинту API.
    Яндекс.Практикума.
    """
    try:
        response = requests.get(ENDPOINT, params=params_list)
    except Exception as error:
        message = f'Ошибка при запросе к основному API: {error}'
        raise Exception(message)
    if response.status_code != HTTPStatus.OK:
        message = f'Ошибка {response.status_code}'
        raise Exception(message)
    return response.json()


for params_list in generate_params():
    print(get_api_answer(params_list))
