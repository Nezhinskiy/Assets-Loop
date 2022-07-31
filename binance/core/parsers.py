from datetime import datetime
from http import HTTPStatus
from itertools import combinations, product

import requests


class BasicParser(object):
    endpoint = None
    Exchanges = None
    Updates = None
    round_to = 6
    records_to_update = []
    records_to_create = []

    def converts_choices_to_set(self, choices: tuple[tuple[str, str]]
                                ) -> set[str]:
        """repackaging choices into a set."""
        return {choice[0] for choice in choices}

    def bulk_update_or_create(self, new_update):
        pass

    def get_all_api_answers(self):
        start_time = datetime.now()
        new_update = self.Updates.objects.create()
        self.bulk_update_or_create(new_update)
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()


class BankParser(BasicParser):
    fiats = None
    buy_and_sell = True

    def generate_unique_params(self) -> list[dict[str]]:
        """Repackaging a tuple with tuples into a list with params."""
        fiats = self.converts_choices_to_set(self.fiats)
        fiats_combinations = tuple(combinations(fiats, 2))  # 2: currency pair
        params_list = [dict([('from', params[0]), ('to', params[-1])])
                       for params in fiats_combinations]
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

    def extract_buy_and_sell_from_json(self, json_data) -> tuple[float, float]:
        pass

    def extract_price_from_json(self, json_data) -> float:
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

    def calculates_price_data(
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

    def choice_buy_and_sell_or_price(self, params):
        if self.buy_and_sell:
            return self.calculates_buy_and_sell_data(params)
        return self.calculates_price_data(params)

    def bulk_update_or_create(self, new_update):
        for params in self.generate_unique_params():
            for value_dict in self.choice_buy_and_sell_or_price(params):
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
                    self.records_to_update.append(update_object)
                else:
                    created_object = self.Exchanges(
                        from_fiat=value_dict['from_fiat'],
                        to_fiat=value_dict['to_fiat'],
                        price=price,
                        update=new_update
                    )
                    self.records_to_create.append(created_object)
        self.Exchanges.objects.bulk_create(self.records_to_create)
        self.Exchanges.objects.bulk_update(self.records_to_update,
                                           ['price', 'update'])


class P2PParser(BasicParser):
    assets = None
    fiats = None
    pay_types = None
    trade_types = None
    page = None
    rows = None

    def create_body(self, asset, trade_type, fiat, pay_types):
        pass

    def create_headers(self, body):
        pass

    def get_api_answer(self, asset, trade_type, fiat, pay_types):
        """Делает запрос к эндпоинту API Tinfoff."""
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

    def extract_price_from_json(self, json_data: dict) -> int:
        pass

    def get_exception(self, fiat, pay_type):
        if fiat == 'RUB' and pay_type == 'Wise':
            return True

    def bulk_update_or_create(self, new_update):
        for asset, trade_type, fiat, pay_type in product(
                self.converts_choices_to_set(self.assets),
                self.converts_choices_to_set(self.trade_types),
                self.converts_choices_to_set(self.fiats),
                self.converts_choices_to_set(self.pay_types)
        ):
            if self.get_exception(fiat, pay_type):
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
                self.records_to_update.append(updated_object)
            else:
                created_object = self.Exchanges(
                    asset=asset, trade_type=trade_type, fiat=fiat,
                    pay_type=pay_type, price=price,
                    update=new_update
                )
                self.records_to_create.append(created_object)
        self.Exchanges.objects.bulk_create(self.records_to_create)
        self.Exchanges.objects.bulk_update(self.records_to_update,
                                           ['price', 'update'])
