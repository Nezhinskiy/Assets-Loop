from http import HTTPStatus
from itertools import combinations
from typing import List

import requests


class BankParser(object):
    fiats = None
    endpoint = None
    model = None
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

    def extract_buy_and_sell_from_json(self, json_data: dict) -> list[float]:
        pass

    def calculates_buy_and_sell_data(self, params):
        buy_and_sell = self.extract_buy_and_sell_from_json(
            self.get_api_answer(params))
        buy_data = list(params.values())
        buy_data.append(round(buy_and_sell[0], self.round_to))
        sell_data = list(params.values())
        sell_data.reverse()
        sell_data.append(round(1.0 / buy_and_sell[1], self.round_to))
        return [buy_data, sell_data]

    def get_all_api_answers(self):
        for params in self.generate_unique_params():
            q = self.calculates_buy_and_sell_data(params)

            print(q)

