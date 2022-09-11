from __future__ import annotations

from datetime import datetime
from http import HTTPStatus
from itertools import combinations, permutations, product

import requests

from banks.models import Banks, BanksExchangeRates, BanksExchangeRatesUpdates
from crypto_exchanges.models import (CryptoExchanges, IntraCryptoExchanges,
                                     IntraCryptoExchangesUpdates,
                                     P2PCryptoExchangesRates,
                                     P2PCryptoExchangesRatesUpdates,
                                     Card2Fiat2CryptoExchanges,
                                     Card2Fiat2CryptoExchangesUpdates)


class BankParser(object):
    bank_name = None
    endpoint = None
    fiats = None
    buy_and_sell = True
    name_from = 'from'
    name_to = 'to'
    ROUND_TO = 10
    CURRENCY_PAIR = 2

    def converts_choices_to_set(self, choices: tuple[tuple[str, str]]
                                ) -> set[str]:
        """repackaging choices into a set."""
        return {choice[0] for choice in choices}

    def create_params(self, fiats_combinations):
        pass

    def generate_unique_params(self) -> list[dict[str]]:
        """Repackaging a tuple with tuples into a list with params."""
        from banks.banks_config import BANKS_CONFIG
        bank_config = BANKS_CONFIG.get(self.bank_name)
        currencies = bank_config.get('currencies')
        random_currencies = set(currencies)
        currencies_combinations = tuple(
            combinations(
                random_currencies, self.CURRENCY_PAIR
            ) if self.buy_and_sell else permutations(
                random_currencies, self.CURRENCY_PAIR
            )
        )
        params_list = self.create_params(currencies_combinations)
        return params_list

    def get_api_answer(self, params):
        """Делает запрос к эндпоинту API Tinfoff."""
        try:
            response = requests.get(self.endpoint, params)
        except Exception as error:
            message = f'Ошибка при запросе к основному API: {error}'
            raise Exception(message)
        if response.status_code != HTTPStatus.OK:
            message = f'Ошибка {response.status_code}, params: {params}, endpoint: {self.endpoint}'
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
    crypto_exchange_name = None
    assets = None
    fiats = None
    pay_types = None
    trade_types = None
    page = None
    rows = None
    endpoint = None
    ROUND_TO = 10
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
            self, crypto_exchange, new_update, records_to_update,
            records_to_create, asset, trade_type, fiat, pay_type, price
    ):
        target_object = P2PCryptoExchangesRates.objects.filter(
            crypto_exchange=crypto_exchange, asset=asset, trade_type=trade_type,
            fiat=fiat, pay_type=pay_type
        )
        if target_object.exists():
            updated_object = P2PCryptoExchangesRates.objects.get(
                crypto_exchange=crypto_exchange, asset=asset,
                trade_type=trade_type, fiat=fiat, pay_type=pay_type
            )
            if updated_object.price == price:
                return
            updated_object.price = price
            updated_object.update = new_update
            records_to_update.append(updated_object)
        else:
            created_object = P2PCryptoExchangesRates(
                crypto_exchange=crypto_exchange, asset=asset,
                trade_type=trade_type, fiat=fiat, pay_type=pay_type,
                price=price, update=new_update
            )
            records_to_create.append(created_object)

    def get_all_api_answers(self, crypto_exchange, new_update,
                            records_to_update, records_to_create):
        from crypto_exchanges.crypto_exchanges_config import (
            CRYPTO_EXCHANGES_CONFIG)
        crypto_exchanges_configs = CRYPTO_EXCHANGES_CONFIG.get(
            self.crypto_exchange_name)
        assets = crypto_exchanges_configs.get('assets')
        trade_types = crypto_exchanges_configs.get('trade_types')
        fiats = crypto_exchanges_configs.get('fiats')
        pay_types = crypto_exchanges_configs.get('pay_types')
        for asset, trade_type, fiat, pay_type in product(assets, trade_types,
                                                         fiats, pay_types):
            if self.get_exception(fiat, pay_type):
                continue
            response = self.get_api_answer(asset, trade_type,
                                           fiat, pay_type)
            price = self.extract_price_from_json(response)
            self.add_to_bulk_update_or_create(
                crypto_exchange, new_update, records_to_update,
                records_to_create, asset, trade_type, fiat, pay_type, price
            )

    def main(self):
        start_time = datetime.now()
        if not CryptoExchanges.objects.filter(
                name=self.crypto_exchange_name
        ).exists():
            CryptoExchanges.objects.create(name=self.crypto_exchange_name)
        crypto_exchange = CryptoExchanges.objects.get(
            name=self.crypto_exchange_name
        )
        new_update = P2PCryptoExchangesRatesUpdates.objects.create(
            crypto_exchange=crypto_exchange
        )
        records_to_update = []
        records_to_create = []
        self.get_all_api_answers(crypto_exchange, new_update, records_to_update,
                                 records_to_create)
        P2PCryptoExchangesRates.objects.bulk_create(records_to_create)
        P2PCryptoExchangesRates.objects.bulk_update(records_to_update,
                                                    ['price', 'update'])
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()


class CryptoExchangesParser(BankParser):
    crypto_exchange_name = None

    def calculates_buy_and_sell_data(self, params) -> tuple[dict, dict]:
        buy_and_sell = self.extract_buy_and_sell_from_json(
            self.get_api_answer(params))
        buy_data = {
            'from_asset': params[self.name_from],
            'to_asset': params[self.name_to],
            'price': round(buy_and_sell[0], self.ROUND_TO)
        }
        sell_data = {
            'from_asset': params[self.name_to],
            'to_asset': params[self.name_from],
            'price': round(1.0 / buy_and_sell[1], self.ROUND_TO)
        }
        return buy_data, sell_data

    def calculates_price_data(self, params) -> list[dict]:
        price = self.extract_price_from_json(self.get_api_answer(params))
        price_data = {
            'from_asset': params[self.name_from],
            'to_asset': params[self.name_to],
            'price': round(price, self.ROUND_TO)
        }
        return [price_data]

    def generate_unique_params(self) -> list[tuple[str]]:
        """Repackaging a tuple with tuples into a list with params."""
        from crypto_exchanges.crypto_exchanges_config import (
            CRYPTO_EXCHANGES_CONFIG)
        crypto_exchanges_configs = CRYPTO_EXCHANGES_CONFIG.get(
            self.crypto_exchange_name)
        assets = crypto_exchanges_configs.get('assets')
        currencies_combinations = list(combinations(
            assets, self.CURRENCY_PAIR
        ) if self.buy_and_sell else permutations(assets, self.CURRENCY_PAIR))
        crypto_fiats = crypto_exchanges_configs.get('crypto_fiats')
        for crypto_fiat in crypto_fiats:
            for asset in assets:
                currencies_combinations.append((asset, crypto_fiat))
        params_list = self.create_params(currencies_combinations)
        return params_list

    def add_to_bulk_update_or_create(
            self, crypto_exchange, new_update, records_to_update,
            records_to_create, value_dict, price
    ):
        target_object = IntraCryptoExchanges.objects.filter(
            crypto_exchange=crypto_exchange,
            from_asset=value_dict['from_asset'],
            to_asset=value_dict['to_asset']
        )
        if target_object.exists():
            updated_object = IntraCryptoExchanges.objects.get(
                crypto_exchange=crypto_exchange,
                from_asset=value_dict['from_asset'],
                to_asset=value_dict['to_asset']
            )
            if updated_object.price == price:
                return
            updated_object.price = price
            updated_object.update = new_update
            records_to_update.append(updated_object)
        else:
            created_object = IntraCryptoExchanges(
                crypto_exchange=crypto_exchange,
                from_asset=value_dict['from_asset'],
                to_asset=value_dict['to_asset'],
                price=price,
                update=new_update
            )
            records_to_create.append(created_object)

    def get_all_api_answers(
            self, crypto_exchange, new_update, records_to_update,
            records_to_create
    ):
        for params in self.generate_unique_params():
            for value_dict in self.choice_buy_and_sell_or_price(params):
                price = value_dict.pop('price')
                self.add_to_bulk_update_or_create(
                    crypto_exchange, new_update, records_to_update,
                    records_to_create, value_dict, price
                )

    def main(self):
        start_time = datetime.now()
        if not CryptoExchanges.objects.filter(
                name=self.crypto_exchange_name
        ).exists():
            CryptoExchanges.objects.create(name=self.crypto_exchange_name)
        crypto_exchange = CryptoExchanges.objects.get(
            name=self.crypto_exchange_name
        )
        new_update = IntraCryptoExchangesUpdates.objects.create(
            crypto_exchange=crypto_exchange
        )
        records_to_update = []
        records_to_create = []
        self.get_all_api_answers(crypto_exchange, new_update,
                                 records_to_update, records_to_create)
        IntraCryptoExchanges.objects.bulk_create(records_to_create)
        IntraCryptoExchanges.objects.bulk_update(records_to_update,
                                                 ['price', 'update'])
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()


class Card2Fiat2CryptoExchangesParser:

    def __init__(self, crypto_exchange_name, round_to=10):
        self.crypto_exchange_name = crypto_exchange_name
        self.ROUND_TO = round_to

    def calculates_price(self, fiat, asset, transaction_fee, trade_type):
        fiat_price = 1 - transaction_fee / 100
        if trade_type == 'BUY':
            crypto_price = IntraCryptoExchanges.objects.get(
                from_asset=fiat, to_asset=asset).price
        else:  # SELL
            crypto_price = IntraCryptoExchanges.objects.get(
                from_asset=asset, to_asset=fiat).price
        price = round(fiat_price * crypto_price, self.ROUND_TO)
        return price

    def generate_all_datas(self, fiat, asset, method, trade_type) -> dict:
        data = {
            'asset': asset,
            'fiat': fiat,
            'trade_type': trade_type,
            'transaction_method': method[0]
        }
        return data

    def main_loop(self, fiats, assets, trade_type, crypto_exchange, new_update,
                  records_to_update, records_to_create):
        for fiat, methods in fiats.items():
            for method, asset in product(methods, assets):
                value_dict = self.generate_all_datas(fiat, asset, method,
                                                     trade_type)
                price = self.calculates_price(fiat, asset, method[1],
                                              trade_type)
                self.add_to_bulk_update_or_create(
                    crypto_exchange, new_update, records_to_update,
                    records_to_create, value_dict, price)

    def get_all_datas(self, crypto_exchange, new_update, records_to_update,
                      records_to_create):
        from crypto_exchanges.crypto_exchanges_config import (
            CRYPTO_EXCHANGES_CONFIG)
        crypto_exchanges_configs = CRYPTO_EXCHANGES_CONFIG.get(
            self.crypto_exchange_name)
        assets = crypto_exchanges_configs.get('assets')
        deposit_fiats = crypto_exchanges_configs.get('deposit_fiats')
        trade_type = 'BUY'
        self.main_loop(deposit_fiats, assets, trade_type, crypto_exchange,
                       new_update, records_to_update, records_to_create)
        withdraw_fiats = crypto_exchanges_configs.get('withdraw_fiats')
        trade_type = 'SELL'
        self.main_loop(withdraw_fiats, assets, trade_type, crypto_exchange,
                       new_update, records_to_update, records_to_create)

    def add_to_bulk_update_or_create(
            self, crypto_exchange, new_update, records_to_update,
            records_to_create, value_dict, price
    ):
        target_object = Card2Fiat2CryptoExchanges.objects.filter(
            crypto_exchange=crypto_exchange,
            asset=value_dict['asset'],
            fiat=value_dict['fiat'],
            trade_type=value_dict['trade_type'],
            transaction_method=value_dict['transaction_method']
        )
        if target_object.exists():
            updated_object = Card2Fiat2CryptoExchanges.objects.get(
                crypto_exchange=crypto_exchange,
                asset=value_dict['asset'],
                fiat=value_dict['fiat'],
                trade_type=value_dict['trade_type'],
                transaction_method=value_dict['transaction_method']
            )
            if updated_object.price == price:
                return
            updated_object.price = price
            updated_object.update = new_update
            records_to_update.append(updated_object)
        else:
            created_object = Card2Fiat2CryptoExchanges(
                crypto_exchange=crypto_exchange,
                asset=value_dict['asset'],
                fiat=value_dict['fiat'],
                trade_type=value_dict['trade_type'],
                transaction_method=value_dict['transaction_method'],
                price=price,
                update=new_update
            )
            records_to_create.append(created_object)

    def main(self):
        start_time = datetime.now()
        if not CryptoExchanges.objects.filter(
                name=self.crypto_exchange_name
        ).exists():
            CryptoExchanges.objects.create(name=self.crypto_exchange_name)
        crypto_exchange = CryptoExchanges.objects.get(
            name=self.crypto_exchange_name
        )
        new_update = Card2Fiat2CryptoExchangesUpdates.objects.create(
            crypto_exchange=crypto_exchange
        )
        records_to_update = []
        records_to_create = []
        self.get_all_datas(crypto_exchange, new_update,
                           records_to_update, records_to_create)
        Card2Fiat2CryptoExchanges.objects.bulk_create(records_to_create)
        Card2Fiat2CryptoExchanges.objects.bulk_update(records_to_update,
                                                      ['price', 'update'])
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()
