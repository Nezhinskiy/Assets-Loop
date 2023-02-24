from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, time, timedelta, timezone
from http import HTTPStatus
from itertools import combinations, permutations, product
from sys import getsizeof
from typing import List, Tuple, Dict

from banks.models import (Banks, BanksExchangeRates, BanksExchangeRatesUpdates,
                          CurrencyMarkets)
from crypto_exchanges.models import (CryptoExchanges, IntraCryptoExchanges,
                                     IntraCryptoExchangesUpdates,
                                     ListsFiatCrypto, ListsFiatCryptoUpdates,
                                     P2PCryptoExchangesRates,
                                     P2PCryptoExchangesRatesUpdates)
from core.tor import Tor
import logging

from arbitration.settings import DATA_OBSOLETE_IN_MINUTES


class BaseParser(ABC):
    endpoint = None

    def __init__(self) -> None:
        from banks.banks_config import BANKS_CONFIG
        self.logger = logging.getLogger(self.__class__.__name__)
        self.start_time = datetime.now()
        self.records_to_update = []
        self.records_to_create = []
        self.banks_config = BANKS_CONFIG
        self.duration = None

    def logger_start(self) -> None:
        message = f'Start {self.__class__.__name__} at {self.start_time}.'
        self.logger.error(message)

    def logger_end(self) -> None:
        message1 = f'Finish {self.__class__.__name__} at {self.duration}.'
        self.logger.error(message1)
        message2 = (
            f'{self.__class__.__name__} updated: '
            f'{len(self.records_to_update) + len(self.records_to_create)}'
        )
        self.logger.error(message2)


class ParsingViaTor(BaseParser, ABC):
    LIMIT_TRY = 3

    def __init__(self) -> None:
        super().__init__()
        self.tor = Tor()
        self.count_try = 0

    def get_api_answer_post(self, body: dict, headers: dict, endpoint=None
                            ) -> dict | bool:
        self.count_try = 0
        if endpoint is None:
            endpoint = self.endpoint
        while self.count_try < self.LIMIT_TRY:
            try:
                response = self.tor.session.post(endpoint, headers=headers,
                                                 json=body)
            except Exception as error:
                self.unsuccessful_response_handler(error)
                continue
            if response.status_code != HTTPStatus.OK:
                self.negative_response_status_handler(response)
                continue
            self.successful_response_handler()
            return response.json()
        return False

    def get_api_answer_get(self, params=None, endpoint=None) -> dict | bool:
        self.count_try = 0
        if endpoint is None:
            endpoint = self.endpoint
        while self.count_try < self.LIMIT_TRY:
            try:
                response = self.tor.session.get(endpoint, params=params)
            except Exception as error:
                self.unsuccessful_response_handler(error)
                continue
            if response.status_code != HTTPStatus.OK:
                self.negative_response_status_handler(response)
                continue
            self.successful_response_handler()
            return response.json()
        return False

    def unsuccessful_response_handler(self, error) -> None:
        message = (f'{error} with class: '
                   f'{self.__class__.__name__}, count try: {self.count_try}')
        self.logger.error(message)
        self.tor.renew_connection()
        self.count_try += 1

    def negative_response_status_handler(self, response) -> None:
        message = (f'{response.status_code} with class: '
                   f'{self.__class__.__name__}, count try: {self.count_try}')
        self.logger.error(message)
        self.tor.renew_connection()
        self.count_try += 1

    def successful_response_handler(self) -> None:
        message = (f'Successful response with class: '
                   f'{self.__class__.__name__}')
        self.logger.info(message)


class CryptoParser(ParsingViaTor, ABC):
    crypto_exchange_name: str

    def __init__(self) -> None:
        super().__init__()
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        self.crypto_exchanges_configs = CRYPTO_EXCHANGES_CONFIG.get(
            self.crypto_exchange_name)
        self.assets = set(self.crypto_exchanges_configs.get('assets'))
        self.all_fiats = set(CRYPTO_EXCHANGES_CONFIG.get('all_fiats'))
        self.crypto_exchange = CryptoExchanges.objects.get(
            name=self.crypto_exchange_name
        )

    @staticmethod
    def create_headers(body: dict) -> dict:
        return {
            'Content-Type': 'application/json',
            'Content-Length': str(getsizeof(body))
        }


class BankParser(ParsingViaTor, ABC):
    model = BanksExchangeRates
    model_update = BanksExchangeRatesUpdates
    bank_name: str
    endpoint: str
    buy_and_sell: bool
    name_from: str
    name_to: str
    CURRENCY_PAIR = 2

    def __init__(self) -> None:
        super().__init__()
        self.bank = Banks.objects.get(name=self.bank_name)
        self.new_update = self.model_update.objects.create(bank=self.bank)

    @abstractmethod
    def create_params(self, fiats_combinations: tuple) -> list[dict[str]]:
        pass

    def generate_unique_params(self) -> list[dict[str]]:
        """Repackaging a tuple with tuples into a list with params."""
        bank_config = self.banks_config.get(self.bank_name)
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

    def get_api_answer(self, params: dict) -> dict:
        """Делает запрос к эндпоинту API Tinfoff."""
        response = self.get_api_answer_get(params)
        return response

    def extract_buy_and_sell_from_json(self, json_data: dict) -> tuple[float,
                                                                       float]:
        pass

    def extract_price_from_json(self, json_data: dict) -> float:
        pass

    def calculates_buy_and_sell_data(self, params: dict) -> tuple[dict, dict]:
        buy_and_sell = self.extract_buy_and_sell_from_json(
            self.get_api_answer(params))
        try:
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
        except Exception as error:
            message = (f'Error with calculates buy and sell data in '
                       f'{self.__class__.__name__}. Data: {params}, '
                       f'{buy_and_sell}. Error: {error}')
            self.logger.error(message)

    def calculates_price_data(self, params: dict) -> list[dict]:
        price = self.extract_price_from_json(self.get_api_answer(params))
        try:
            price_data = {
                'from_fiat': params[self.name_from],
                'to_fiat': params[self.name_to],
                'price': price
            }
            return [price_data]
        except Exception as error:
            message = (f'Error with calculates price data in '
                       f'{self.__class__.__name__}. Data: {params}. '
                       f'Error: {error}')
            self.logger.error(message)

    def choice_buy_and_sell_or_price(self, params
                                     ) -> tuple[dict, dict] | list[dict]:
        if self.buy_and_sell:
            return self.calculates_buy_and_sell_data(params)
        return self.calculates_price_data(params)

    def add_to_bulk_update_or_create(self, value_dict: dict, price: float
                                     ) -> None:
        target_object = BanksExchangeRates.objects.filter(
            bank=self.bank, from_fiat=value_dict['from_fiat'],
            to_fiat=value_dict['to_fiat'], currency_market__isnull=True
        )
        if target_object.exists():
            updated_object = target_object.get()
            updated_object.price = price
            updated_object.update = self.new_update
            self.records_to_update.append(updated_object)
        else:
            BanksExchangeRates.objects.create(
                bank=self.bank, from_fiat=value_dict['from_fiat'],
                to_fiat=value_dict['to_fiat'], price=price,
                update=self.new_update
            )

    def get_all_api_answers(self) -> None:
        for params in self.generate_unique_params():
            values = self.choice_buy_and_sell_or_price(params)
            if not values:
                continue
            for value_dict in values:
                price = value_dict.pop('price')
                self.add_to_bulk_update_or_create(value_dict, price)

    def main(self) -> None:
        self.get_all_api_answers()
        BanksExchangeRates.objects.bulk_update(self.records_to_update,
                                               ['price', 'update'])
        self.duration = datetime.now() - self.start_time
        self.new_update.duration = self.duration
        self.new_update.save()


class BankInvestParser(ParsingViaTor, ABC):
    model = BanksExchangeRates
    model_update = BanksExchangeRatesUpdates
    currency_markets_name: str
    endpoint: str
    link_ends: str

    def __init__(self) -> None:
        super().__init__()
        self.currency_market = CurrencyMarkets.objects.get(
            name=self.currency_markets_name)
        self.new_update = self.model_update.objects.create(
            currency_market=self.currency_market
        )

    def add_to_bulk_update_or_create(self, value_dict: dict) -> None:
        bank_names = []
        for name, value in self.banks_config.items():
            if self.currency_markets_name in value['bank_invest_exchanges']:
                bank_names.append(name)
        for bank_name in bank_names:
            bank = Banks.objects.get(name=bank_name)
            price = value_dict['price']
            target_object = BanksExchangeRates.objects.filter(
                bank=bank,
                currency_market=self.currency_market,
                from_fiat=value_dict['from_fiat'],
                to_fiat=value_dict['to_fiat']
            )
            if target_object.exists():
                updated_object = target_object.get()
                updated_object.price = price
                updated_object.update = self.new_update
                self.records_to_update.append(updated_object)
            else:
                created_object = BanksExchangeRates(
                    bank=bank,
                    currency_market=self.currency_market,
                    from_fiat=value_dict['from_fiat'],
                    to_fiat=value_dict['to_fiat'],
                    price=price,
                    update=self.new_update
                )
                self.records_to_create.append(created_object)

    @abstractmethod
    def get_all_api_answers(self) -> None:
        pass

    def main(self) -> None:
        self.get_all_api_answers()
        self.model.objects.bulk_create(self.records_to_create)
        self.model.objects.bulk_update(self.records_to_update,
                                       ['price', 'update'])
        self.duration = datetime.now() - self.start_time
        self.new_update.duration = self.duration
        self.new_update.save()


class P2PParser(CryptoParser, ABC):
    model = P2PCryptoExchangesRates
    model_update = P2PCryptoExchangesRatesUpdates
    crypto_exchange_name: str
    bank_name: str
    page: int
    rows: int
    endpoint: str
    CURRENCY_PAIR = 2
    payment_channel = 'P2P'

    def __init__(self) -> None:
        super().__init__()
        self.bank = Banks.objects.get(name=self.bank_name)
        self.new_update = self.model_update.objects.create(
            crypto_exchange=self.crypto_exchange, bank=self.bank,
            payment_channel=self.payment_channel
        )
        self.full_update = None
        self.trade_types = self.crypto_exchanges_configs.get('trade_types')
        self.banks_configs = self.banks_config[self.bank_name]
        self.fiats = set(self.banks_configs['currencies'])

    @abstractmethod
    def create_body(self, asset: str, trade_type: str, fiat: str) -> dict:
        pass

    @staticmethod
    @abstractmethod
    def extract_price_from_json(json_data: dict) -> float | None:
        pass

    def get_api_answer(self, asset: str, trade_type: str, fiat: str) -> dict:
        """Делает запрос к эндпоинту API."""
        body = self.create_body(asset, trade_type, fiat)
        headers = self.create_headers(body)
        response = self.get_api_answer_post(body, headers)
        return response

    def add_to_bulk_update_or_create(
            self, asset: str, trade_type: str, fiat: str, price: float
    ) -> None:
        target_object = P2PCryptoExchangesRates.objects.filter(
            crypto_exchange=self.crypto_exchange, asset=asset,
            trade_type=trade_type, fiat=fiat, bank=self.bank,
            payment_channel=self.payment_channel
        )
        if target_object.exists():
            updated_object = target_object.get()
            updated_object.price = price
            updated_object.update = self.new_update
            self.records_to_update.append(updated_object)
        else:
            created_object = P2PCryptoExchangesRates(
                crypto_exchange=self.crypto_exchange, asset=asset,
                trade_type=trade_type, fiat=fiat, bank=self.bank,
                price=price, update=self.new_update,
                payment_channel=self.payment_channel
            )
            self.records_to_create.append(created_object)

    def get_all_api_answers(self) -> None:
        for fiat in self.fiats:
            assets = self.crypto_exchanges_configs['assets_for_fiats'].get(fiat
                                                                           )
            if not assets:
                assets = self.crypto_exchanges_configs['assets_for_fiats'
                                                       ]['all']
            for trade_type, asset in product(self.trade_types, set(assets)):
                if not self.full_update:
                    target_rates = P2PCryptoExchangesRates.objects.filter(
                        crypto_exchange=self.crypto_exchange,
                        asset=asset, trade_type=trade_type, fiat=fiat,
                        bank=self.bank, payment_channel=self.payment_channel
                    )
                    if target_rates.exists() and not target_rates.get().price:
                        continue
                response = self.get_api_answer(asset, fiat, trade_type)
                if response is False:
                    continue
                price = self.extract_price_from_json(response)
                if price is not None:
                    price = 1 / price if trade_type == 'BUY' else price
                self.add_to_bulk_update_or_create(asset, trade_type, fiat,
                                                  price)

    def is_full_update(self) -> None:
        if (
                self.model_update.objects.filter(
                payment_channel=self.payment_channel).count() == 0
                or datetime.now(timezone.utc).time().hour
                != self.model_update.objects.last().updated.time().hour
        ):
            self.full_update = True

    def main(self) -> None:
        self.is_full_update()
        self.get_all_api_answers()
        self.model.objects.bulk_create(self.records_to_create)
        self.model.objects.bulk_update(self.records_to_update,
                                       ['price', 'update'])
        self.duration = datetime.now() - self.start_time
        self.new_update.duration = self.duration
        self.new_update.save()


class CryptoExchangesParser(BaseParser, ABC):
    model = IntraCryptoExchanges
    model_update = IntraCryptoExchangesUpdates
    crypto_exchange_name: str
    name_from: str
    exceptions: tuple[str]
    CURRENCY_PAIR = 2

    def __init__(self) -> None:
        super().__init__()
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        self.crypto_exchange = CryptoExchanges.objects.get(
            name=self.crypto_exchange_name
        )
        self.new_update = self.model_update.objects.create(
            crypto_exchange=self.crypto_exchange
        )
        self.crypto_exchanges_configs = CRYPTO_EXCHANGES_CONFIG.get(
            self.crypto_exchange_name)
        self.assets = self.crypto_exchanges_configs.get('assets')
        self.crypto_fiats = self.crypto_exchanges_configs.get('crypto_fiats')

    @abstractmethod
    def create_params(self, fiats_combinations: tuple) -> list[dict[str]]:
        pass

    @abstractmethod
    def get_api_answer(self, params: dict) -> dict:
        pass

    @staticmethod
    @abstractmethod
    def extract_price_from_json(json_data: dict) -> float:
        pass

    @abstractmethod
    def calculates_buy_and_sell_data(self, params) -> tuple[dict, dict] | None:
        pass

    def generate_unique_params(self) -> list[dict[str]]:
        """Repackaging a tuple with tuples into a list with params."""
        currencies_combinations = list(combinations(self.assets,
                                                    self.CURRENCY_PAIR))
        invalid_params_list = self.crypto_exchanges_configs.get(
            'invalid_params_list')
        for crypto_fiat in self.crypto_fiats:
            for asset in self.assets:
                currencies_combinations.append((asset, crypto_fiat))
        currencies_combinations = tuple(
            currencies_combination for currencies_combination
            in currencies_combinations
            if currencies_combination not in invalid_params_list
        )
        params_list = self.create_params(currencies_combinations)
        return params_list

    def add_to_bulk_update_or_create(self, value_dict: dict, price: float
                                     ) -> None:
        target_object = IntraCryptoExchanges.objects.filter(
            crypto_exchange=self.crypto_exchange,
            from_asset=value_dict['from_asset'],
            to_asset=value_dict['to_asset']
        )
        if target_object.exists():
            updated_object = IntraCryptoExchanges.objects.get(
                crypto_exchange=self.crypto_exchange,
                from_asset=value_dict['from_asset'],
                to_asset=value_dict['to_asset']
            )
            updated_object.price = price
            updated_object.update = self.new_update
            self.records_to_update.append(updated_object)
        else:
            IntraCryptoExchanges.objects.create(
                crypto_exchange=self.crypto_exchange,
                from_asset=value_dict['from_asset'],
                to_asset=value_dict['to_asset'],
                price=price, spot_fee=value_dict['spot_fee'],
                update=self.new_update
            )

    def get_all_api_answers(self):
        for params in self.generate_unique_params():
            values = self.calculates_buy_and_sell_data(params)
            if not values:
                continue
            for value_dict in values:
                price = value_dict.pop('price')
                self.add_to_bulk_update_or_create(value_dict, price)

    def main(self) -> None:
        self.get_all_api_answers()
        self.model.objects.bulk_update(self.records_to_update,
                                       ['price', 'update'])
        self.duration = datetime.now() - self.start_time
        self.new_update.duration = self.duration
        self.new_update.save()


class Card2Wallet2CryptoExchangesParser(CryptoParser, ABC):
    model = P2PCryptoExchangesRates
    model_update = P2PCryptoExchangesRatesUpdates
    payment_channel = 'Card2Wallet2CryptoExchange'
    data_obsolete_in_minutes: int = DATA_OBSOLETE_IN_MINUTES
    crypto_exchange_name: str

    def __init__(self, trade_type: str) -> None:
        super().__init__()
        self.new_update = self.model_update.objects.create(
            crypto_exchange=self.crypto_exchange,
            payment_channel=self.payment_channel
        )
        self.trade_type = trade_type
        self.deposit_fiats = self.crypto_exchanges_configs.get('deposit_fiats')
        self.withdraw_fiats = self.crypto_exchanges_configs.get(
            'withdraw_fiats')
        self.invalid_params_list = self.crypto_exchanges_configs.get(
            'invalid_params_list')
        self.update_time = datetime.now(timezone.utc) - timedelta(
            minutes=self.data_obsolete_in_minutes
        )

    def calculates_price_and_intra_crypto_exchange(
            self, fiat: str, asset: str, transaction_fee: float
    ) -> tuple:
        fiat_price = 1 - transaction_fee / 100
        if self.trade_type == 'BUY':
            intra_crypto_exchange = IntraCryptoExchanges.objects.get(
                from_asset=fiat, to_asset=asset)
            crypto_price = intra_crypto_exchange.price
        else:  # SELL
            intra_crypto_exchange = IntraCryptoExchanges.objects.get(
                from_asset=asset, to_asset=fiat)
            crypto_price = intra_crypto_exchange.price
        price = fiat_price * crypto_price
        return price, intra_crypto_exchange

    def generate_all_datas(self, fiat: str, asset: str,
                           transaction_method: str,
                           transaction_fee: float) -> dict:
        return {
            'asset': asset,
            'fiat': fiat,
            'trade_type': self.trade_type,
            'transaction_method': transaction_method,
            'transaction_fee': transaction_fee
        }

    def check_p2p_exchange_is_better_or_false(
            self, value_dict: dict, price: float, bank: Banks
    ) -> bool:
        p2p_exchange = self.model.objects.filter(
            crypto_exchange=self.crypto_exchange, bank=bank,
            asset=value_dict['asset'], trade_type=value_dict['trade_type'],
            fiat=value_dict['fiat'], payment_channel='P2P',
            price__isnull=False, update__updated__gte=self.update_time
        )
        if p2p_exchange.exists():
            p2p_price = p2p_exchange.get().price
            if (
                    value_dict['trade_type'] == 'BUY' and price > p2p_price
                    or value_dict['trade_type'] == 'SELL'
                    and price < p2p_price
            ):
                return True
        return False

    def get_all_datas(self) -> None:
        fiats = (self.deposit_fiats if self.trade_type == 'BUY'
                 else self.withdraw_fiats)
        for fiat, methods in fiats.items():
            for method, asset in product(methods, self.assets):
                if ((fiat, asset) in self.invalid_params_list or (asset, fiat)
                        in self.invalid_params_list):
                    continue
                transaction_method, transaction_fee = method
                value_dict = self.generate_all_datas(
                    fiat, asset, transaction_method, transaction_fee
                )
                price, intra_crypto_exchange = (
                    self.calculates_price_and_intra_crypto_exchange(
                        fiat, asset, transaction_fee
                    )
                )
                self.add_to_bulk_update_or_create(
                    value_dict, price, intra_crypto_exchange
                )

    def add_to_bulk_update_or_create(
            self, value_dict: dict, price: float,
            intra_crypto_exchange: IntraCryptoExchanges
    ) -> None:
        bank_names = []
        for name, value in self.banks_config.items():
            if self.payment_channel in value['payment_channels']:
                bank_names.append(name)
        for bank_name in bank_names:
            bank = Banks.objects.get(name=bank_name)
            target_object = self.model.objects.filter(
                crypto_exchange=self.crypto_exchange, bank=bank,
                asset=value_dict['asset'], trade_type=value_dict['trade_type'],
                fiat=value_dict['fiat'],
                transaction_method=value_dict['transaction_method'],
                intra_crypto_exchange=intra_crypto_exchange,
                payment_channel=self.payment_channel
            )
            if self.check_p2p_exchange_is_better_or_false(value_dict, price,
                                                          bank):
                if target_object.exists():
                    target_object.delete()
                return
            if target_object.exists():
                updated_object = target_object.get()
                updated_object.price = price
                updated_object.transaction_fee = value_dict['transaction_fee']
                updated_object.update = self.new_update
                self.records_to_update.append(updated_object)
            else:
                created_object = self.model(
                    crypto_exchange=self.crypto_exchange, bank=bank,
                    asset=value_dict['asset'], fiat=value_dict['fiat'],
                    trade_type=value_dict['trade_type'],
                    transaction_method=value_dict['transaction_method'],
                    transaction_fee=value_dict['transaction_fee'],
                    price=price, intra_crypto_exchange=intra_crypto_exchange,
                    payment_channel=self.payment_channel,
                    update=self.new_update
                )
                self.records_to_create.append(created_object)

    def main(self):
        self.get_all_datas()
        P2PCryptoExchangesRates.objects.bulk_create(self.records_to_create)
        P2PCryptoExchangesRates.objects.bulk_update(
            self.records_to_update, ['price', 'update', 'transaction_fee']
        )
        self.duration = datetime.now() - self.start_time
        self.new_update.duration = self.duration
        self.new_update.save()


class ListsFiatCryptoParser(CryptoParser, ABC):
    model = ListsFiatCrypto
    model_update = ListsFiatCryptoUpdates
    crypto_exchange_name: str
    endpoint_sell: str
    endpoint_buy: str

    def __init__(self) -> None:
        super().__init__()
        self.new_update = self.model_update.objects.create(
            crypto_exchange=self.crypto_exchange
        )

    @staticmethod
    def create_body_sell(asset: str) -> dict:
        return {
            "channels": ["card"],
            "crypto": asset,
            "transactionType": "SELL"
        }

    @staticmethod
    def create_body_buy(fiat: str) -> dict:
        return {
            "channels": ["card"],
            "fiat": fiat,
            "transactionType": "BUY"
        }

    def extract_buy_or_sell_list_from_json(self, json_data: dict,
                                           trade_type: str) -> List[list]:
        general_list = json_data.get('data')
        valid_asset = self.assets if trade_type == 'BUY' else self.all_fiats
        if general_list == '':
            return []
        valid_list = []
        for asset_data in general_list:
            asset = asset_data.get('assetCode')
            if asset_data.get('quotation') != '' and asset in valid_asset:
                max_limit = int(float(asset_data['maxLimit']) * 0.9)
                valid_list.append([asset, max_limit])
        return valid_list

    def get_api_answer(self, asset=None, fiat=None) -> dict:
        """Делает запрос к эндпоинту API Tinfoff."""
        if asset:
            body = self.create_body_sell(asset)
            endpoint = self.endpoint_sell
        else:  # if fiat
            body = self.create_body_buy(fiat)
            endpoint = self.endpoint_buy
        headers = self.create_headers(body)
        response = self.get_api_answer_post(body, headers, endpoint=endpoint)
        return response

    def add_to_update_or_create(self, list_fiat_crypto: dict, trade_type: str
                                ) -> None:
        target_object = ListsFiatCrypto.objects.filter(
            crypto_exchange=self.crypto_exchange, trade_type=trade_type
        )
        if target_object.exists():
            updated_object = ListsFiatCrypto.objects.get(
                crypto_exchange=self.crypto_exchange, trade_type=trade_type
            )
            if updated_object.list_fiat_crypto == list_fiat_crypto:
                return
            updated_object.list_fiat_crypto = list_fiat_crypto
            updated_object.update = self.new_update
            updated_object.save()
        else:
            created_object = ListsFiatCrypto(
                crypto_exchange=self.crypto_exchange,
                list_fiat_crypto=list_fiat_crypto,
                trade_type=trade_type,
                update=self.new_update
            )
            created_object.save()

    def get_all_api_answers(self) -> None:
        sell_dict = {}
        for asset in self.assets:
            response_sell = self.get_api_answer(asset=asset)
            if response_sell is False:
                continue
            sell_list = self.extract_buy_or_sell_list_from_json(response_sell,
                                                                'SELL')
            sell_dict[asset] = sell_list

        buy_dict = {}
        for fiat in self.all_fiats:
            response_buy = self.get_api_answer(fiat=fiat)
            if response_buy is False:
                continue
            buy_list = self.extract_buy_or_sell_list_from_json(response_buy,
                                                               'BUY')
            for asset_info in buy_list:
                fiat_list = []
                if asset_info[0] not in buy_dict:
                    buy_dict[asset_info[0]] = fiat_list
                buy_dict[asset_info[0]].append([fiat, asset_info[1]])

        self.add_to_update_or_create(sell_dict, trade_type='SELL')
        self.add_to_update_or_create(buy_dict, trade_type='BUY')

    def main(self) -> None:
        if self.model_update.objects.all().count() != 0:
            if (self.model_update.objects.last().updated.date()
                    == datetime.now(timezone.utc).date()):
                return
        self.get_all_api_answers()
        self.duration = datetime.now() - self.start_time
        self.new_update.duration = self.duration
        self.new_update.save()


class Card2CryptoExchangesParser(CryptoParser, ABC):
    model = P2PCryptoExchangesRates
    model_update = P2PCryptoExchangesRatesUpdates
    payment_channel = 'Card2CryptoExchange'
    transaction_method = 'Bank Card (Visa/MC)'
    endpoint_sell: str
    endpoint_buy: str

    def __init__(self, trade_type: str) -> None:
        super().__init__()
        self.new_update = self.model_update.objects.create(
            crypto_exchange=self.crypto_exchange,
            payment_channel=self.payment_channel
        )
        self.trade_type = trade_type
        self.full_update = None

    @staticmethod
    def create_body_sell(fiat: str, asset: str, amount: int) -> dict:
        return {
            "baseCurrency": fiat,
            "cryptoCurrency": asset,
            "payType": "Ask",
            "paymentChannel": "card",
            "rail": "card",
            "requestedAmount": amount,
            "requestedCurrency": fiat
        }

    @staticmethod
    def create_body_buy(fiat: str, asset: str, amount: int) -> dict:
        return {
            "baseCurrency": fiat,
            "cryptoCurrency": asset,
            "payType": "Ask",
            "paymentChannel": "card",
            "rail": "card",
            "requestedAmount": amount,
            "requestedCurrency": fiat
        }

    @staticmethod
    def create_params_buy(fiat: str, asset: str) -> dict:
        return {
            'channelCode': 'card',
            'fiatCode': fiat,
            'cryptoAsset': asset
        }

    def extract_values_from_json(self, json_data: dict, amount: int
                                 ) -> tuple | None:
        if self.trade_type == 'SELL':
            data = json_data['data'].get('rows')
            pre_price = data.get('quotePrice')
            if not pre_price:
                return
            commission = data.get('totalFee') / amount
            price = pre_price / (1 + commission)
            commission *= 100
        else:  # BUY
            data = json_data['data']
            pre_price = data['price']
            if not pre_price:
                return
            pre_price = float(pre_price)
            commission = 0.02
            price = 1 / (pre_price * (1 + commission))
            commission *= 100
        return price, pre_price, commission

    def get_api_answer(self, asset: str, fiat: str, amount: int) -> dict:
        """Делает запрос к эндпоинту API Tinfoff."""
        if self.trade_type == 'SELL':
            body = self.create_body_sell(fiat, asset, amount)
            headers = self.create_headers(body)
            response = self.get_api_answer_post(
                body, headers, endpoint=self.endpoint_sell
            )
        else:
            params = self.create_params_buy(fiat, asset)
            response = self.get_api_answer_get(
                params, endpoint=self.endpoint_buy
            )
        return response

    def add_to_bulk_update_or_create(self, asset: str, fiat: str, price: float,
                                     pre_price: float, transaction_fee: float
                                     ) -> None:
        bank_names = []
        for name, value in self.banks_config.items():
            if self.payment_channel in value['payment_channels']:
                bank_names.append(name)
        for bank_name in bank_names:
            bank = Banks.objects.get(name=bank_name)
            target_object = P2PCryptoExchangesRates.objects.filter(
                crypto_exchange=self.crypto_exchange, bank=bank, asset=asset,
                trade_type=self.trade_type, fiat=fiat,
                transaction_method=self.transaction_method,
                payment_channel=self.payment_channel
            )
            p2p_exchange = P2PCryptoExchangesRates.objects.filter(
                crypto_exchange=self.crypto_exchange, bank=bank,
                asset=asset,
                trade_type=self.trade_type, fiat=fiat,
                payment_channel='P2P', price__isnull=False
            )
            if p2p_exchange.exists():
                p2p_price = p2p_exchange.get().price
                if (
                        self.trade_type == 'BUY' and price > p2p_price
                        or self.trade_type == 'SELL' and price < p2p_price
                ):
                    if target_object.exists():
                        target_object.delete()
                    return
            if target_object.exists():
                updated_object = target_object.get()
                updated_object.price = price
                updated_object.pre_price = pre_price
                updated_object.transaction_fee = transaction_fee
                updated_object.update = self.new_update
                self.records_to_update.append(updated_object)
            else:
                created_object = P2PCryptoExchangesRates(
                    crypto_exchange=self.crypto_exchange, bank=bank,
                    asset=asset, trade_type=self.trade_type, fiat=fiat,
                    price=price, pre_price=pre_price,
                    transaction_fee=transaction_fee, update=self.new_update,
                    payment_channel=self.payment_channel,
                    transaction_method=self.transaction_method,
                )
                self.records_to_create.append(created_object)

    def get_all_api_answers(self) -> None:
        list_fiat_crypto = ListsFiatCrypto.objects.get(
            crypto_exchange=self.crypto_exchange, trade_type=self.trade_type
        ).list_fiat_crypto
        for asset in self.assets:
            fiats_info = list_fiat_crypto.get(asset)
            if fiats_info is None:
                continue
            for fiat_info in fiats_info:
                fiat, amount = fiat_info
                if fiat == 'RUB' and self.trade_type == 'BUY':
                    continue
                if not self.full_update:
                    target_rates = P2PCryptoExchangesRates.objects.filter(
                        crypto_exchange=self.crypto_exchange,
                        asset=asset, trade_type=self.trade_type, fiat=fiat,
                        payment_channel=self.payment_channel
                    )
                    if not target_rates.exists():
                        continue
                response = self.get_api_answer(asset, fiat, amount)
                if not response:
                    continue
                values = self.extract_values_from_json(response, amount)
                if not values:
                    continue
                price, pre_price, commission = values
                self.add_to_bulk_update_or_create(
                    asset, fiat, price, pre_price, commission
                )

    def is_full_update(self) -> None:
        self.full_update = True
        if (
                self.model_update.objects.filter(
                payment_channel=self.payment_channel).count() == 0
                or datetime.now(timezone.utc).time().hour
                != self.model_update.objects.last().updated.time().hour
        ):
            self.full_update = True

    def main(self) -> None:
        self.is_full_update()
        self.get_all_api_answers()
        self.model.objects.bulk_create(self.records_to_create)
        self.model.objects.bulk_update(
            self.records_to_update,
            ['price', 'pre_price', 'transaction_fee', 'update']
        )
        self.duration = datetime.now() - self.start_time
        self.new_update.duration = self.duration
        self.new_update.save()
