from __future__ import annotations

from datetime import datetime
from http import HTTPStatus
from itertools import combinations, permutations, product
from sys import getsizeof
from typing import List

import requests

from banks.models import (BankInvestExchanges, BankInvestExchangesUpdates,
                          Banks, BanksExchangeRates, BanksExchangeRatesUpdates,
                          CurrencyMarkets)
from crypto_exchanges.models import (Card2CryptoExchanges,
                                     Card2CryptoExchangesUpdates,
                                     Card2Wallet2CryptoExchanges,
                                     Card2Wallet2CryptoExchangesUpdates,
                                     CryptoExchanges, IntraCryptoExchanges,
                                     IntraCryptoExchangesUpdates,
                                     ListsFiatCrypto, ListsFiatCryptoUpdates,
                                     P2PCryptoExchangesRates,
                                     P2PCryptoExchangesRatesUpdates)


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
            'price': buy_and_sell[0]
        }
        sell_data = {
            'from_fiat': params[self.name_to],
            'to_fiat': params[self.name_from],
            'price': 1 / buy_and_sell[1]
        }
        return buy_data, sell_data

    def extract_price_from_json(self, json_data: list) -> float:
        pass

    def calculates_price_data(self, params) -> list[dict]:
        price = self.extract_price_from_json(self.get_api_answer(params))
        price_data = {
            'from_fiat': params[self.name_from],
            'to_fiat': params[self.name_to],
            'price': price
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
            binance_name = (self.bank_name if self.bank_name != 'Tinkoff'
                            else 'TinkoffNew')
            Banks.objects.create(name=self.bank_name, binance_name=binance_name)
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

    def create_body(self, asset, trade_type, fiat, bank):
        pass

    def create_headers(self, body):
        pass

    def extract_price_from_json(self, json_data: dict) -> float | None:
        pass

    def get_api_answer(self, asset, trade_type, fiat, bank):
        """Делает запрос к эндпоинту API Tinfoff."""
        body = self.create_body(asset, trade_type, fiat, bank)
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
            records_to_create, asset, trade_type, fiat, bank_object, price
    ):
        target_object = P2PCryptoExchangesRates.objects.filter(
            crypto_exchange=crypto_exchange, asset=asset, trade_type=trade_type,
            fiat=fiat, bank=bank_object
        )
        if target_object.exists():
            updated_object = P2PCryptoExchangesRates.objects.get(
                crypto_exchange=crypto_exchange, asset=asset,
                trade_type=trade_type, fiat=fiat, bank=bank_object
            )
            if updated_object.price == price:
                return
            updated_object.price = price
            updated_object.update = new_update
            records_to_update.append(updated_object)
        else:
            created_object = P2PCryptoExchangesRates(
                crypto_exchange=crypto_exchange, asset=asset,
                trade_type=trade_type, fiat=fiat, bank=bank_object,
                price=price, update=new_update
            )
            records_to_create.append(created_object)

    def get_all_api_answers(self, crypto_exchange, new_update,
                            records_to_update, records_to_create):
        from banks.banks_config import BANKS_CONFIG
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        crypto_exchanges_configs = CRYPTO_EXCHANGES_CONFIG.get(
            self.crypto_exchange_name)
        trade_types = crypto_exchanges_configs.get('trade_types')
        banks = BANKS_CONFIG.keys()
        for bank in banks:
            bank_object = Banks.objects.get(name=bank)
            bank_name = bank_object.binance_name
            banks_configs = BANKS_CONFIG[bank]
            fiats = banks_configs['currencies']
            for fiat in fiats:
                assets = crypto_exchanges_configs['assets_for_fiats'].get(fiat)
                if not assets:
                    assets = crypto_exchanges_configs['assets_for_fiats']['all']
                for trade_type, asset in product(trade_types, assets):
                    response = self.get_api_answer(asset, trade_type,
                                                   fiat, bank_name)
                    price = (
                        1 / self.extract_price_from_json(response)
                        if trade_type == 'BUY'
                        and self.extract_price_from_json(response) is not None
                        else self.extract_price_from_json(response)
                    )

                    self.add_to_bulk_update_or_create(
                        crypto_exchange, new_update, records_to_update,
                        records_to_create, asset, trade_type, fiat, bank_object,
                        price
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
            self.get_api_answer(params)
        )
        buy_data = {
            'from_asset': params[self.name_from],
            'to_asset': params[self.name_to],
            'price': buy_and_sell[0]
        }
        sell_data = {
            'from_asset': params[self.name_to],
            'to_asset': params[self.name_from],
            'price': 1 / buy_and_sell[1]
        }
        return buy_data, sell_data

    def calculates_price_data(self, params) -> list[dict]:
        price = self.extract_price_from_json(self.get_api_answer(params))
        price_data = {
            'from_asset': params[self.name_from],
            'to_asset': params[self.name_to],
            'price': price
        }
        return [price_data]

    def generate_unique_params(self) -> list[tuple[str]]:
        """Repackaging a tuple with tuples into a list with params."""
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        crypto_exchanges_configs = CRYPTO_EXCHANGES_CONFIG.get(
            self.crypto_exchange_name)
        assets = crypto_exchanges_configs.get('assets')
        currencies_combinations = list(combinations(
            assets, self.CURRENCY_PAIR
        ) if self.buy_and_sell else permutations(assets, self.CURRENCY_PAIR))
        crypto_fiats = crypto_exchanges_configs.get('crypto_fiats')
        invalid_params_list = crypto_exchanges_configs.get(
            'invalid_params_list')
        for crypto_fiat in crypto_fiats:
            for asset in assets:
                currencies_combinations.append((asset, crypto_fiat))
        currencies_combinations = [
            currencies_combination for currencies_combination
            in currencies_combinations
            if currencies_combination not in invalid_params_list
        ]
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


class Card2Wallet2CryptoExchangesParser:

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
        price = fiat_price * crypto_price
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
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        crypto_exchanges_configs = CRYPTO_EXCHANGES_CONFIG.get(
            self.crypto_exchange_name)
        for fiat, methods in fiats.items():
            for method, asset in product(methods, assets):
                invalid_params_list = crypto_exchanges_configs.get(
                    'invalid_params_list')
                if ((fiat, asset) in invalid_params_list or (asset, fiat)
                        in invalid_params_list):
                    continue
                value_dict = self.generate_all_datas(fiat, asset, method,
                                                     trade_type)
                price = self.calculates_price(fiat, asset, method[1],
                                              trade_type)
                self.add_to_bulk_update_or_create(
                    crypto_exchange, new_update, records_to_update,
                    records_to_create, value_dict, price)

    def get_all_datas(self, crypto_exchange, new_update, records_to_update,
                      records_to_create):
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
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
        target_object = Card2Wallet2CryptoExchanges.objects.filter(
            crypto_exchange=crypto_exchange,
            asset=value_dict['asset'],
            fiat=value_dict['fiat'],
            trade_type=value_dict['trade_type'],
            transaction_method=value_dict['transaction_method']
        )
        if target_object.exists():
            updated_object = Card2Wallet2CryptoExchanges.objects.get(
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
            created_object = Card2Wallet2CryptoExchanges(
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
        new_update = Card2Wallet2CryptoExchangesUpdates.objects.create(
            crypto_exchange=crypto_exchange
        )
        records_to_update = []
        records_to_create = []
        self.get_all_datas(crypto_exchange, new_update,
                           records_to_update, records_to_create)
        Card2Wallet2CryptoExchanges.objects.bulk_create(records_to_create)
        Card2Wallet2CryptoExchanges.objects.bulk_update(records_to_update,
                                                        ['price', 'update'])
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()


class ListsFiatCryptoParser(object):
    crypto_exchange_name = None
    endpoint_sell = None
    endpoint_buy = None

    def create_body_sell(self, asset):
        return {
            "channels": ["card"],
            "crypto": asset,
            "transactionType": "SELL"
        }

    def create_body_buy(self, fiat):
        return {
            "channels": ["card"],
            "fiat": fiat,
            "transactionType": "BUY"
        }

    def create_headers(self, body):
        return {
            "Content-Type": "application/json",
            "Content-Length": str(getsizeof(body)),
        }

    def extract_sell_list_from_json(self, json_data: dict, fiats
                                    ) -> List[list]:
        general_sell_list = json_data.get('data')
        valid_sell_list = []
        for fiat_data in general_sell_list:
            fiat = fiat_data.get('assetCode')
            if fiat_data.get('quotation') != '' and fiat in fiats:  # rate exists
                max_limit = int(float(fiat_data['maxLimit']) * 0.9)
                valid_sell_list.append([fiat, max_limit])
        return valid_sell_list

    def extract_buy_list_from_json(self, json_data: dict, assets
                                   ) -> List[list]:
        general_buy_list = json_data.get('data')
        if general_buy_list == '':
            return []
        valid_buy_list = []
        for fiat_data in general_buy_list:
            asset = fiat_data.get('assetCode')
            if fiat_data.get('quotation') != '' and asset in assets:  # rate exists
                max_limit = int(float(fiat_data['maxLimit']) * 0.9)
                valid_buy_list.append([asset, max_limit])
        return valid_buy_list

    def get_api_answer(self, asset=None, fiat=None):
        """Делает запрос к эндпоинту API Tinfoff."""
        if asset:
            body = self.create_body_sell(asset)
            endpoint = self.endpoint_sell
        else:  # if fiat
            body = self.create_body_buy(fiat)
            endpoint = self.endpoint_buy
        headers = self.create_headers(body)
        try:
            response = requests.post(endpoint, headers=headers, json=body)
        except Exception as error:
            message = f'Ошибка при запросе к основному API: {error}'
            raise Exception(message)
        if response.status_code != HTTPStatus.OK:
            message = f'Ошибка {response.status_code}'
            raise Exception(message)
        return response.json()

    def add_to_update_or_create(
            self, crypto_exchange, new_update, list_fiat_crypto, trade_type
    ):
        target_object = ListsFiatCrypto.objects.filter(
            crypto_exchange=crypto_exchange, trade_type=trade_type
        )
        if target_object.exists():
            updated_object = ListsFiatCrypto.objects.get(
                crypto_exchange=crypto_exchange, trade_type=trade_type
            )
            if updated_object.list_fiat_crypto == list_fiat_crypto:
                return
            updated_object.list_fiat_crypto = list_fiat_crypto
            updated_object.update = new_update
            updated_object.save()
        else:
            created_object = ListsFiatCrypto(
                crypto_exchange=crypto_exchange,
                list_fiat_crypto=list_fiat_crypto,
                trade_type=trade_type,
                update=new_update
            )
            created_object.save()

    def get_all_api_answers(self, crypto_exchange, new_update):
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        crypto_exchanges_configs = CRYPTO_EXCHANGES_CONFIG.get(
            self.crypto_exchange_name)
        assets = crypto_exchanges_configs.get('assets')
        fiats = CRYPTO_EXCHANGES_CONFIG.get('all_fiats')
        sell_dict = {}
        buy_dict = {}

        for asset in assets:
            response_sell = self.get_api_answer(asset=asset)
            sell_list = self.extract_sell_list_from_json(response_sell, fiats)
            sell_dict[asset] = sell_list

        for fiat in fiats:
            response_buy = self.get_api_answer(fiat=fiat)
            buy_list = self.extract_buy_list_from_json(response_buy, assets)
            for asset_info in buy_list:
                fiat_list = []
                if asset_info[0] not in buy_dict:
                    buy_dict[asset_info[0]] = fiat_list
                buy_dict[asset_info[0]].append([fiat, asset_info[1]])

        self.add_to_update_or_create(
            crypto_exchange, new_update, sell_dict, trade_type='SELL'
        )
        self.add_to_update_or_create(
            crypto_exchange, new_update, buy_dict, trade_type='BUY'
        )

    def main(self):
        start_time = datetime.now()
        crypto_exchange = CryptoExchanges.objects.get(
            name=self.crypto_exchange_name
        )
        new_update = ListsFiatCryptoUpdates.objects.create(
            crypto_exchange=crypto_exchange
        )
        self.get_all_api_answers(crypto_exchange, new_update)
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()


class Card2CryptoExchangesParser(object):
    crypto_exchange_name = None
    endpoint_sell = None
    endpoint_buy = None
    ROUND_TO = 5

    def converts_choices_to_set(self, choices: tuple[tuple[str, str]]
                                ) -> set[str]:
        """repackaging choices into a set."""
        return {choice[0] for choice in choices}

    def create_body_sell(self, fiat, asset, amount):
        return {
            "baseCurrency": fiat,
            "cryptoCurrency": asset,
            "payType": "Ask",
            "paymentChannel": "card",
            "rail": "card",
            "requestedAmount": amount,
            "requestedCurrency": fiat
        }

    def create_body_buy(self, fiat, asset, amount):
        return {
            "baseCurrency": fiat,
            "cryptoCurrency": asset,
            "payType": "Ask",
            "paymentChannel": "card",
            "rail": "card",
            "requestedAmount": amount,
            "requestedCurrency": fiat
        }

    def create_params_buy(self, fiat, asset):
        return {
            'channelCode': 'card',
            'fiatCode': fiat,
            'cryptoAsset': asset
        }

    def create_headers(self, body):
        return {
            "Content-Type": "application/json",
            "Content-Length": str(getsizeof(body)),
        }

    def extract_values_from_json(self, json_data: dict, amount, trade_type
                                 ) -> [int | None]:
        if trade_type == 'SELL':
            data = json_data['data'].get('rows')
            pre_price = data.get('quotePrice')
            commission = data.get('totalFee') / amount
            price = pre_price / (1 + commission)
            commission *= 100
        else:  # BUY
            data = json_data['data']
            pre_price = float(data['price'])
            commission = 0.02
            price = 1 / (pre_price * (1 + commission))
            commission *= 100
        return price, pre_price, commission

    def get_api_answer(self, asset, trade_type, fiat, amount):
        """Делает запрос к эндпоинту API Tinfoff."""
        if trade_type == 'SELL':
            body = self.create_body_sell(fiat, asset, amount)
            endpoint = self.endpoint_sell
            headers = self.create_headers(body)
            try:
                response = requests.post(endpoint, headers=headers, json=body)
            except Exception as error:
                message = f'Ошибка при запросе к основному API: {error}'
                raise Exception(message)
        else:
            params = self.create_params_buy(fiat, asset)
            endpoint = self.endpoint_buy
            try:
                response = requests.get(endpoint, params)
            except Exception as error:
                message = f'Ошибка при запросе к основному API: {error}'
                raise Exception(message)
        if response.status_code != HTTPStatus.OK:
            message = f'Ошибка {response.status_code}'
            raise Exception(message)
        return response.json()

    def add_to_bulk_update_or_create(
            self, crypto_exchange, new_update, records_to_update,
            records_to_create, asset, trade_type, fiat, price, pre_price,
            commission
    ):
        target_object = Card2CryptoExchanges.objects.filter(
            crypto_exchange=crypto_exchange, asset=asset, trade_type=trade_type,
            fiat=fiat
        )
        if target_object.exists():
            updated_object = Card2CryptoExchanges.objects.get(
                crypto_exchange=crypto_exchange, asset=asset,
                trade_type=trade_type, fiat=fiat
            )
            if updated_object.price == price:
                return
            updated_object.price = price
            updated_object.pre_price = pre_price
            updated_object.commission = commission
            updated_object.update = new_update
            records_to_update.append(updated_object)
        else:
            created_object = Card2CryptoExchanges(
                crypto_exchange=crypto_exchange, asset=asset,
                trade_type=trade_type, fiat=fiat, price=price,
                pre_price=pre_price, commission=commission, update=new_update
            )
            records_to_create.append(created_object)

    def get_all_api_answers(self, crypto_exchange, new_update,
                            records_to_update, records_to_create):
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        crypto_exchanges_configs = CRYPTO_EXCHANGES_CONFIG.get(
            self.crypto_exchange_name)
        assets = crypto_exchanges_configs.get('assets')
        trade_types = crypto_exchanges_configs.get('trade_types')
        for trade_type in trade_types:
            list_fiat_crypto = ListsFiatCrypto.objects.get(
                crypto_exchange=crypto_exchange, trade_type=trade_type
            ).list_fiat_crypto
            for asset in assets:
                fiats_info = list_fiat_crypto.get(asset)
                for fiat_info in fiats_info:
                    fiat, amount = fiat_info
                    if fiat == 'RUB' and trade_type == 'BUY':
                        continue
                    response = self.get_api_answer(asset, trade_type, fiat,
                                                   amount)
                    price, pre_price, commission = (
                        self.extract_values_from_json(response, amount,
                                                      trade_type))
                    self.add_to_bulk_update_or_create(
                        crypto_exchange, new_update, records_to_update,
                        records_to_create, asset, trade_type, fiat, price,
                        pre_price, commission
                    )

    def main(self):
        start_time = datetime.now()
        crypto_exchange = CryptoExchanges.objects.get(
            name=self.crypto_exchange_name
        )
        new_update = Card2CryptoExchangesUpdates.objects.create(
            crypto_exchange=crypto_exchange
        )
        records_to_update = []
        records_to_create = []
        self.get_all_api_answers(crypto_exchange, new_update, records_to_update,
                                 records_to_create)
        Card2CryptoExchanges.objects.bulk_create(records_to_create)
        Card2CryptoExchanges.objects.bulk_update(
            records_to_update, ['price', 'pre_price', 'commission', 'update']
        )
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()


class BankInvestParser(object):
    def __init__(self, currency_markets_name, endpoint, link_ends):
        self.currency_markets_name = currency_markets_name
        self.currency_market = CurrencyMarkets.objects.get(
            name=currency_markets_name)
        self.endpoint = endpoint
        self.link_ends = link_ends

    def get_api_answer(self, link_end):
        """Делает запрос к эндпоинту API Tinfoff."""
        try:
            response = requests.get(self.endpoint + link_end)
        except Exception as error:
            message = f'Ошибка при запросе к основному API: {error}'
            raise Exception(message)
        if response.status_code != HTTPStatus.OK:
            message = f'Ошибка {response.status_code}'
            raise Exception(message)
        return response.json()

    def extract_buy_and_sell_from_json(self, json_data: dict, link_end):
        items = json_data['payload']['items']
        for item in items:
            content = item['content']
            instruments = content['instruments']
            for instrument in instruments:
                if not instrument:
                    continue
                ticker = instrument.get('ticker')
                if ticker == link_end:
                    price = instrument['price']
                    break
        if link_end[0:3] == 'KZT':
            price /= 100
        elif link_end[0:3] == 'AMD':
            price /= 100
        buy_price = price - price * 0.003
        sell_price = (1 / price) - (1 / price) * 0.003
        return buy_price, sell_price

    def calculates_buy_and_sell_data(self, link_end,
                                     answer) -> tuple[dict, dict]:
        buy_price, sell_price = self.extract_buy_and_sell_from_json(answer,
                                                                    link_end)
        buy_data = {
            'from_fiat': link_end[0:3],
            'to_fiat': link_end[3:6],
            'price': buy_price
        }
        sell_data = {
            'from_fiat': link_end[3:6],
            'to_fiat': link_end[0:3],
            'price': sell_price
        }
        return buy_data, sell_data

    def add_to_bulk_update_or_create(
            self, new_update, records_to_update, records_to_create, value_dict
    ):
        price = value_dict['price']
        target_object = BankInvestExchanges.objects.filter(
            currency_market=self.currency_market,
            from_fiat=value_dict['from_fiat'],
            to_fiat=value_dict['to_fiat']
        )
        if target_object.exists():
            updated_object = target_object.get()
            if updated_object.price == price:
                return
            updated_object.price = price
            updated_object.update = new_update
            records_to_update.append(updated_object)
        else:
            created_object = BankInvestExchanges(
                currency_market=self.currency_market,
                from_fiat=value_dict['from_fiat'],
                to_fiat=value_dict['to_fiat'],
                price=price,
                update=new_update
            )
            records_to_create.append(created_object)

    def get_all_api_answers(self, new_update, records_to_update,
                            records_to_create):
        for link_end in self.link_ends:
            answer = self.get_api_answer(link_end)
            buy_and_sell_data = self.calculates_buy_and_sell_data(link_end,
                                                                  answer)
            for buy_or_sell_data in buy_and_sell_data:
                self.add_to_bulk_update_or_create(
                    new_update, records_to_update, records_to_create,
                    buy_or_sell_data
                )

    def main(self):
        start_time = datetime.now()
        new_update = BankInvestExchangesUpdates.objects.create(
            currency_market=self.currency_market
        )
        records_to_update = []
        records_to_create = []
        self.get_all_api_answers(new_update, records_to_update,
                                 records_to_create)
        BankInvestExchanges.objects.bulk_create(records_to_create)
        BankInvestExchanges.objects.bulk_update(records_to_update,
                                                ['price', 'update'])
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()
