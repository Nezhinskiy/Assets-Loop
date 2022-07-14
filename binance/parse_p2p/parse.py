import logging
import time
from http import HTTPStatus
from os import getenv
from sys import getsizeof
from typing import Dict, List
import requests

ENDPOINT = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
stringData = {
    "page": 1,
    "rows": 20,
    "publisherType": None,
    "asset": "USDT",
    "tradeType": "BUY",
    "fiat": "RUB",
    "payTypes": ["Tinkoff"]
}

HEADERS = {
        "Content-Type": "application/json",
        "Content-Length": str(getsizeof(stringData)),
      }


def get_api_answer():
    """Делает запрос к единственному эндпоинту API.
    Яндекс.Практикума.
    """

    try:
        response = requests.post(ENDPOINT, headers=HEADERS, json=stringData)
    except Exception as error:
        message = f'Ошибка при запросе к основному API: {error}'
        raise Exception(message)
    if response.status_code != HTTPStatus.OK:
        message = f'Ошибка {response.status_code}'
        raise Exception(message)
    return response.json()

print(get_api_answer())

