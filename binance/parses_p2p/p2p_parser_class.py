from datetime import datetime, timedelta
from http import HTTPStatus
from sys import getsizeof

import requests

from parses_p2p.models import (ASSETS, FIATS, PAY_TYPES, TRADE_TYPES,
                               P2PBinance, UpdateP2PBinance)


class P2PParser(object):
    assets = None
    fiats = None
    pay_types = None
    trade_types = None
    endpoint = None
    page = None
    rows = None
    Exchanges = None
    Updates = None
    round_to = 6

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

    def get_api_answer(self, asset, trade_type, fiat, pay_types):
        """Делает запрос к единственному эндпоинту API.
        Яндекс.Практикума.
        """
        body = self.create_body(asset, trade_type, fiat, pay_types)
        headers = self.create_headers(body)
        try:
            response = requests.post(self.endpoint, headers=headers, json=body)
        except Exception as error:
            message = f'Ошибка при запросе к основному API: {error}'
            raise Exception(message)
        if response.status_code != HTTPStatus.OK:
            message = f'Ошибка {response.status_code}'
            raise Exception(message)
        return response.json()

    def extract_price_from_json(self, json_data: dict):
        data = json_data.get('data')
        if len(data) == 0:
            price = None
            return price
        internal_data = data[0]
        adv = internal_data.get('adv')
        price = adv.get('price')
        return price

    def converts_choices_to_set(self, choices: tuple[tuple[int, int]]
                                ) -> set[str]:
        return {pair[0] for pair in choices}

    def get_exceptions(self, *args):
        pass

    def p2p_binance_bulk_update_or_create(self, new_update):
        records_to_create = []
        records_to_update = []
        for asset in self.converts_choices_to_set(self.assets):
            for trade_type in self.converts_choices_to_set(self.trade_types):
                for fiat in self.converts_choices_to_set(self.fiats):
                    for pay_type in self.converts_choices_to_set(self.pay_types):
                        if fiat == 'RUB' and pay_type == 'Wise':
                            continue
                        response = self.get_api_answer(asset, trade_type,
                                                       fiat, pay_type)
                        price = self.extract_price_from_json(response)
                        target_object = self.Exchanges.objects.filter(
                            asset=asset, trade_type=trade_type, fiat=fiat,
                            pay_type=pay_type
                        )
                        if target_object.exists():
                            updated_object = self.Exchanges.objects.get(
                                asset=asset, trade_type=trade_type, fiat=fiat,
                                pay_type=pay_type
                            )
                            updated_object.price = price
                            updated_object.update = new_update
                            records_to_update.append(updated_object)
                        else:
                            created_object = self.Exchanges(
                                asset=asset, trade_type=trade_type, fiat=fiat,
                                pay_type=pay_type, price=price,
                                update=new_update
                            )
                            records_to_create.append(created_object)
        self.Exchanges.objects.bulk_create(records_to_create)
        self.Exchanges.objects.bulk_update(records_to_update, ['price', 'update'])

    def get_all_api_answers(self):
        start_time = datetime.now()
        new_update = self.Updates.objects.create()
        self.p2p_binance_bulk_update_or_create(new_update)
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()

#
# ENDPOINT = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
# PAGE = 1
# ROWS = 1
#
#
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
