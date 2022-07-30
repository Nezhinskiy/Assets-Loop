from datetime import datetime, timedelta
from http import HTTPStatus
from sys import getsizeof

import requests
from core.parsers import P2PParser
from parses_p2p.models import (ASSETS, FIATS, PAY_TYPES, TRADE_TYPES,
                               P2PBinance, UpdateP2PBinance)


class BinanceParser(P2PParser):
    assets = ASSETS
    fiats = FIATS
    pay_types = PAY_TYPES
    trade_types = TRADE_TYPES
    endpoint = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
    page = 1
    rows = 1
    Exchanges = P2PBinance
    Updates = UpdateP2PBinance

    def create_body(self, asset, trade_type, fiat, pay_types):
        return {
            "page": self.page,
            "rows": self.rows,
            "publisherType": None,
            "asset": asset,
            "tradeType": trade_type,
            "fiat": fiat,
            "payTypes": [pay_types]
        }

    def create_headers(self, body):
        return {
            "Content-Type": "application/json",
            "Content-Length": str(getsizeof(body)),
        }

    def extract_price_from_json(self, json_data: dict) -> int:
        data = json_data.get('data')
        if len(data) == 0:
            price = None
            return price
        internal_data = data[0]
        adv = internal_data.get('adv')
        price = adv.get('price')
        return price

def get_all():
    binance_parser = BinanceParser()
    message = binance_parser.get_all_api_answers()
    return message

# def create_data(asset, trade_type, fiat, pay_types):
#     data = {
#         "page": PAGE,
#         "rows": ROWS,
#         "publisherType": None,
#         "asset": asset,
#         "tradeType": trade_type,
#         "fiat": fiat,
#         "payTypes": [pay_types]
#     }
#     return data
#
#
# def get_api_answer(data):
#     """Делает запрос к единственному эндпоинту API.
#     Яндекс.Практикума.
#     """
#     headers = {
#         "Content-Type": "application/json",
#         "Content-Length": str(getsizeof(data)),
#     }
#     try:
#         response = requests.post(ENDPOINT, headers=headers, json=data)
#     except Exception as error:
#         message = f'Ошибка при запросе к основному API: {error}'
#         raise Exception(message)
#     if response.status_code != HTTPStatus.OK:
#         message = f'Ошибка {response.status_code}'
#         raise Exception(message)
#     return response.json()
#
#
# def parse_price(response):
#     data = response.get('data')
#     if len(data) == 0:
#         price = None
#         return price
#     data1 = data[0]
#     adv = data1.get('adv')
#     price = adv.get('price')
#     return price
#
#
# def p2p_binance_bulk_update_or_create():
#     start_time = datetime.now()
#     records_to_create = []
#     records_to_update = []
#     new_update = UpdateP2PBinance.objects.create()
#     for asset in ASSETS:
#         asset = asset[0]
#         for trade_type in TRADE_TYPES:
#             trade_type = trade_type[0]
#             for fiat in FIATS:
#                 fiat = fiat[0]
#                 for pay_type in PAY_TYPES:
#                     pay_type = pay_type[0]
#                     if fiat == 'RUB' and pay_type == 'Wise':
#                         continue
#                     new_data = create_data(asset, trade_type,
#                                            fiat, pay_type)
#                     response = get_api_answer(new_data)
#                     price = parse_price(response)
#                     target_object = P2PBinance.objects.filter(
#                         asset=asset, trade_type=trade_type, fiat=fiat,
#                         pay_type=pay_type
#                     )
#                     if target_object.exists():
#                         updated_object = P2PBinance.objects.get(
#                             asset=asset, trade_type=trade_type, fiat=fiat,
#                             pay_type=pay_type
#                         )
#                         updated_object.price = price
#                         updated_object.update = new_update
#                         records_to_update.append(updated_object)
#                     else:
#                         created_object = P2PBinance(
#                             asset=asset, trade_type=trade_type, fiat=fiat,
#                             pay_type=pay_type, price=price, update=new_update
#                         )
#                         records_to_create.append(created_object)
#     P2PBinance.objects.bulk_create(records_to_create)
#     P2PBinance.objects.bulk_update(records_to_update, ['price', 'update'])
#     duration = datetime.now() - start_time
#     new_update.duration = duration
#     new_update.save()
