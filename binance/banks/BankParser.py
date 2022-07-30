from datetime import datetime
from http import HTTPStatus
from itertools import combinations
from typing import List, Tuple, Dict, Any

import requests


class BankParser(object):
    fiats = None
    endpoint = None
    Exchanges = None
    Updates = None
    round_to = 6

    def generate_unique_params(self) -> List[dict[str]]:
        fiats = [fiat[0] for fiat in self.fiats]  # repackaging choices into a list
        fiats_combinations = tuple(combinations(fiats, 2))  # 2: currency pair
        params_list = [dict([('from', params[0]), ('to', params[-1])])
                       for params in fiats_combinations]
        # repackaging a list with tuples into a list with dicts
        return params_list

    def get_api_answer(self, params):
        """Делает запрос к эндпоинту API Tinfoff."""
        try:
            response = requests.get(self.endpoint, params)
        except Exception as error:
            message = f'Ошибка при запросе к основному API: {error}'
            raise Exception(message)
        if response.status_code != HTTPStatus.OK:
            message = f'Ошибка {response.status_code}'
            raise Exception(message)
        return response.json()

    def extract_buy_and_sell_from_json(self, json_data: dict) -> tuple[float]:
        pass

    def calculates_buy_and_sell_data(
            self, params) -> tuple[dict[str, float], dict[str, float]]:
        buy_and_sell = self.extract_buy_and_sell_from_json(
            self.get_api_answer(params))
        buy_data = {
            'from_fiat': params['from'],
            'to_fiat': params['to'],
            'price': round(buy_and_sell[0], self.round_to)
        }
        sell_data = {
            'from_fiat': params['to'],
            'to_fiat': params['from'],
            'price': round(1.0 / buy_and_sell[1], self.round_to)
        }
        return buy_data, sell_data

    def bulk_update_or_create(self, params, new_update):
        records_to_update = []
        records_to_create = []
        for value_dict in self.calculates_buy_and_sell_data(params):
            price = value_dict.pop('price')
            target_object = self.Exchanges.objects.filter(
                from_fiat=value_dict['from_fiat'],
                to_fiat=value_dict['to_fiat']
            )
            if target_object.exists():
                update_object = self.Exchanges.objects.get(
                    from_fiat=value_dict['from_fiat'],
                    to_fiat=value_dict['to_fiat']
                )
                update_object.price = price
                update_object.update = new_update
                records_to_update.append(update_object)
            else:
                created_object = self.Exchanges(
                    from_fiat=value_dict['from_fiat'],
                    to_fiat=value_dict['to_fiat'],
                    price=price,
                    update=new_update
                )
                records_to_create.append(created_object)
        self.Exchanges.objects.bulk_create(records_to_create)
        self.Exchanges.objects.bulk_update(records_to_update,
                                             ['price', 'update'])

    def get_all_api_answers(self):
        start_time = datetime.now()
        new_update = self.Updates.objects.create()
        for params in self.generate_unique_params():
            self.bulk_update_or_create(params, new_update)
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()
