from datetime import datetime
from http import HTTPStatus
from itertools import combinations, permutations, product

import requests

from bank_rates.models import BanksExchangeRates, BanksExchangeRatesUpdates, Banks


class BankParser(object):
    bank_name = None
    endpoint = None
    fiats = None
    buy_and_sell = True
    name_from = 'from'
    name_to = 'to'
    ROUND_TO = 6
    CURRENCY_PAIR = 2

    def converts_choices_to_set(self, choices: tuple[tuple[str, str]]
                                ) -> set[str]:
        """repackaging choices into a set."""
        return {choice[0] for choice in choices}

    def create_params(self, fiats_combinations):
        pass

    def generate_unique_params(self) -> list[dict[str]]:
        """Repackaging a tuple with tuples into a list with params."""
        fiats = self.converts_choices_to_set(self.fiats)
        fiats_combinations = tuple(combinations(fiats, self.CURRENCY_PAIR)
                                   if self.buy_and_sell
                                   else permutations(fiats,
                                                     self.CURRENCY_PAIR))
        params_list = self.create_params(fiats_combinations)
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

    def extract_buy_and_sell_from_json(self, json_data: dict) -> tuple[float,
                                                                       float]:
        pass

    def calculates_buy_and_sell_data(self, params) -> tuple[dict, dict]:
        buy_and_sell = self.extract_buy_and_sell_from_json(
            self.get_api_answer(params))
        buy_data = {
            'from_fiat': params[self.name_from],
            'to_fiat': params[self.name_to],
            'price': round(buy_and_sell[0], self.ROUND_TO)
        }
        sell_data = {
            'from_fiat': params[self.name_to],
            'to_fiat': params[self.name_from],
            'price': round(1.0 / buy_and_sell[1], self.ROUND_TO)
        }
        return buy_data, sell_data

    def extract_price_from_json(self, json_data: list) -> float:
        pass

    def calculates_price_data(self, params) -> list[dict]:
        price = self.extract_price_from_json(self.get_api_answer(params))
        price_data = {
            'from_fiat': params[self.name_from],
            'to_fiat': params[self.name_to],
            'price': round(price, self.ROUND_TO)
        }

        return [price_data]

    def choice_buy_and_sell_or_price(self, params):
        if self.buy_and_sell:
            return self.calculates_buy_and_sell_data(params)
        return self.calculates_price_data(params)

    def add_to_bulk_update_or_create(
            self, bank, new_update, records_to_update, records_to_create,
            value_dict, price
    ):
        target_object = BanksExchangeRates.objects.filter(
            bank=bank,
            from_fiat=value_dict['from_fiat'],
            to_fiat=value_dict['to_fiat']
        )
        if target_object.exists():
            updated_object = BanksExchangeRates.objects.get(
                bank=bank,
                from_fiat=value_dict['from_fiat'],
                to_fiat=value_dict['to_fiat']
            )
            if updated_object.price == price:
                return
            updated_object.price = price
            updated_object.update = new_update
            records_to_update.append(updated_object)
        else:
            created_object = BanksExchangeRates(
                bank=bank,
                from_fiat=value_dict['from_fiat'],
                to_fiat=value_dict['to_fiat'],
                price=price,
                update=new_update
            )
            records_to_create.append(created_object)

    def get_all_api_answers(
            self, bank, new_update, records_to_update, records_to_create
    ):
        for params in self.generate_unique_params():
            for value_dict in self.choice_buy_and_sell_or_price(params):
                price = value_dict.pop('price')
                self.add_to_bulk_update_or_create(
                    bank, new_update, records_to_update, records_to_create,
                    value_dict, price
                )

    def main(self):
        start_time = datetime.now()
        if not Banks.objects.filter(name=self.bank_name).exists():
            Banks.objects.create(name=self.bank_name)
        bank = Banks.objects.get(name=self.bank_name)
        new_update = BanksExchangeRatesUpdates.objects.create(bank=bank)
        records_to_update = []
        records_to_create = []
        self.get_all_api_answers(bank, new_update, records_to_update,
                                 records_to_create)
        BanksExchangeRates.objects.bulk_create(records_to_create)
        BanksExchangeRates.objects.bulk_update(records_to_update,
                                           ['price', 'update'])
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()


class P2PParser(object):
    assets = None
    fiats = None
    pay_types = None
    trade_types = None
    page = None
    rows = None
    endpoint = None
    Exchanges = None
    Updates = None
    ROUND_TO = 6
    CURRENCY_PAIR = 2

    def converts_choices_to_set(self, choices: tuple[tuple[str, str]]
                                ) -> set[str]:
        """repackaging choices into a set."""
        return {choice[0] for choice in choices}

    def create_body(self, asset, trade_type, fiat, pay_types):
        pass

    def create_headers(self, body):
        pass

    def extract_price_from_json(self, json_data: dict) -> [int | None]:
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

    def get_exception(self, fiat, pay_type):
        if fiat == 'RUB' and pay_type == 'Wise':
            return True

    def add_to_bulk_update_or_create(
            self, new_update, records_to_update, records_to_create, asset,
            trade_type, fiat, pay_type, price
    ):
        target_object = self.Exchanges.objects.filter(
            asset=asset, trade_type=trade_type, fiat=fiat, pay_type=pay_type
        )
        if target_object.exists():
            updated_object = self.Exchanges.objects.get(
                asset=asset, trade_type=trade_type, fiat=fiat, pay_type=pay_type
            )
            if updated_object.price == price:
                return
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

    def get_all_api_answers(
            self, new_update, records_to_update, records_to_create
    ):
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
            self.add_to_bulk_update_or_create(
                new_update, records_to_update, records_to_create, asset,
                trade_type, fiat, pay_type, price
            )

    def main(self):
        start_time = datetime.now()
        new_update = self.Updates.objects.create()
        records_to_update = []
        records_to_create = []
        self.get_all_api_answers(new_update, records_to_update,
                                 records_to_create)
        self.Exchanges.objects.bulk_create(records_to_create)
        self.Exchanges.objects.bulk_update(records_to_update,
                                           ['price', 'update'])
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()
