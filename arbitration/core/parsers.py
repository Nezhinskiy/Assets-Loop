from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from http import HTTPStatus
from itertools import combinations, permutations, product
from sys import getsizeof
from typing import Any, Dict, List, Optional

from banks.models import (Banks, BanksExchangeRates, BanksExchangeRatesUpdates,
                          CurrencyMarkets)
from core.loggers import ParsingLogger
from core.tor import Tor
from crypto_exchanges.models import (CryptoExchanges, IntraCryptoExchanges,
                                     IntraCryptoExchangesUpdates,
                                     ListsFiatCrypto, ListsFiatCryptoUpdates,
                                     P2PCryptoExchangesRates,
                                     P2PCryptoExchangesRatesUpdates)


class BaseParser(ParsingLogger, ABC):
    endpoint: str
    updated_fields: List[str]
    bank_name = None

    def __init__(self) -> None:
        from banks.banks_config import BANKS_CONFIG
        super().__init__()
        self.records_to_update = []
        self.records_to_create = []
        self.banks_config = BANKS_CONFIG

    def _get_count_created_objects(self) -> None:
        self.count_created_objects = len(self.records_to_create)

    def _get_count_updated_objects(self) -> None:
        self.count_updated_objects = len(self.records_to_update)

    def _successful_response_handler(self) -> None:
        message = (f'Successful response with class: '
                   f'{self.__class__.__name__}')
        self.logger.info(message)

    def _unsuccessful_response_handler(self, error) -> None:
        message = (f'{error} with response, class: '
                   f'{self.__class__.__name__}.')
        self.logger.error(message)

    def _negative_response_status_handler(self, response) -> None:
        message = (f'{response.status_code} with response, class: '
                   f'{self.__class__.__name__}.')
        self.logger.error(message)

    @abstractmethod
    def _get_all_api_answers(self) -> None:
        pass

    def main(self) -> None:
        try:
            self._logger_start()
            self._get_all_api_answers()
            self.model.objects.bulk_create(self.records_to_create)
            self.model.objects.bulk_update(
                self.records_to_update, self.updated_fields
            )
            self.duration = datetime.now(timezone.utc) - self.start_time
            self.new_update.duration = self.duration
            self.new_update.save()
            self._logger_end()
        except Exception as error:
            self._logger_error(error)
            raise Exception


class ParsingViaTor(BaseParser, ABC):
    LIMIT_TRY = 3

    def __init__(self) -> None:
        super().__init__()
        self.tor = Tor()
        self.count_try = 0

    def _get_api_answer_post(self, body: dict, headers: dict, endpoint=None
                             ) -> dict | bool:
        self.count_try = 0
        if endpoint is None:
            endpoint = self.endpoint
        while self.count_try < self.LIMIT_TRY:
            try:
                response = self.tor.session.post(endpoint, headers=headers,
                                                 json=body)
            except Exception as error:
                self._unsuccessful_response_handler(error)
                continue
            if response.status_code != HTTPStatus.OK:
                self._negative_response_status_handler(response)
                continue
            self._successful_response_handler()
            return response.json()
        return False

    def _get_api_answer_get(self, params=None, endpoint=None) -> dict | bool:
        self.count_try = 0
        if endpoint is None:
            endpoint = self.endpoint
        while self.count_try < self.LIMIT_TRY:
            try:
                response = self.tor.session.get(endpoint, params=params)
            except Exception as error:
                self._unsuccessful_response_handler(error)
                continue
            if response.status_code != HTTPStatus.OK:
                self._negative_response_status_handler(response)
                continue
            self._successful_response_handler()
            return response.json()
        return False

    def _unsuccessful_response_handler(self, error) -> None:
        message = (f'{error} with response, class: '
                   f'{self.__class__.__name__}, count try: {self.count_try}')
        self.logger.error(message)
        self.tor.renew_connection()
        self.count_try += 1

    def _negative_response_status_handler(self, response) -> None:
        message = (f'{response.status_code} with response, class: '
                   f'{self.__class__.__name__}, count try: {self.count_try}')
        self.logger.error(message)
        self.tor.renew_connection()
        self.count_try += 1


class CryptoParser(ParsingViaTor, ABC):
    crypto_exchange_name: str

    def __init__(self) -> None:
        super().__init__()
        from crypto_exchanges.crypto_exchanges_config import (
            CRYPTO_EXCHANGES_CONFIG)
        self.crypto_exchanges_configs = CRYPTO_EXCHANGES_CONFIG.get(
            self.crypto_exchange_name)
        self.assets = set(self.crypto_exchanges_configs.get('assets'))
        self.all_fiats = set(CRYPTO_EXCHANGES_CONFIG.get('all_fiats'))
        self.crypto_exchange = CryptoExchanges.objects.get(
            name=self.crypto_exchange_name
        )

    @staticmethod
    def _create_headers(body: dict) -> dict:
        return {
            'Content-Type': 'application/json',
            'Content-Length': str(getsizeof(body))
        }


class BankParser(ParsingViaTor, ABC):
    model = BanksExchangeRates
    model_update = BanksExchangeRatesUpdates
    updated_fields = ['price', 'update']
    bank_name: str
    endpoint: str
    buy_and_sell: bool
    all_values: bool = False
    name_from: str
    name_to: str
    CURRENCY_PAIR = 2

    def __init__(self) -> None:
        super().__init__()
        self.bank = Banks.objects.get(name=self.bank_name)
        self.new_update = self.model_update.objects.create(bank=self.bank)

    def _create_params(self, fiats_combinations: tuple) -> list[dict[str]]:
        pass

    def _generate_unique_params(self) -> list[dict[str]]:
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
        return self._create_params(currencies_combinations)

    def _extract_buy_and_sell_from_json(self, json_data: dict
                                        ) -> tuple[float, float]:
        pass

    def _extract_price_from_json(self, json_data: dict) -> float:
        pass

    def _extract_all_values_from_json(self, json_data: dict
                                      ) -> Optional[List[Dict[str, Any]]]:
        pass

    def _calculates_buy_and_sell_data(self, params: dict) -> tuple[dict, dict]:
        response_json = self._get_api_answer_get(params)
        buy_and_sell = self._extract_buy_and_sell_from_json(response_json)
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

    def _calculates_price_data(self, params: dict) -> list[dict]:
        response_json = self._get_api_answer_get(params)
        price = self._extract_price_from_json(response_json)
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

    def _calculates_all_values_data(self) -> list[dict[str, Any]] | None:
        response_json = self._get_api_answer_get()
        return self._extract_all_values_from_json(response_json)

    def _choice_buy_and_sell_or_price(self, params=None
                                      ) -> tuple[dict, dict] | list[dict]:
        if self.all_values:
            return self._calculates_all_values_data()
        if self.buy_and_sell:
            return self._calculates_buy_and_sell_data(params)
        return self._calculates_price_data(params)

    def _add_to_bulk_update_or_create(self, value_dict: dict, price: float
                                      ) -> None:
        target_object = self.model.objects.filter(
            bank=self.bank, from_fiat=value_dict['from_fiat'],
            to_fiat=value_dict['to_fiat'], currency_market__isnull=True
        )
        if target_object.exists():
            updated_object = target_object.get()
            updated_object.price = price
            updated_object.update = self.new_update
            self.records_to_update.append(updated_object)
        else:
            created_object = self.model(
                bank=self.bank, from_fiat=value_dict['from_fiat'],
                to_fiat=value_dict['to_fiat'], price=price,
                update=self.new_update
            )
            self.records_to_create.append(created_object)

    def _get_all_api_answers(self) -> None:
        for params in self._generate_unique_params():
            values = self._choice_buy_and_sell_or_price(params)
            if not values:
                continue
            for value_dict in values:
                price = value_dict.pop('price')
                self._add_to_bulk_update_or_create(value_dict, price)


class BankInvestParser(ParsingViaTor, ABC):
    model = BanksExchangeRates
    model_update = BanksExchangeRatesUpdates
    updated_fields = ['price', 'update']
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

    def _get_api_answer(self, link_end: str) -> dict:
        endpoint = self.endpoint + link_end
        return self._get_api_answer_get(endpoint=endpoint)

    @staticmethod
    @abstractmethod
    def _extract_buy_and_sell_from_json(json_data: dict, link_end: str
                                        ) -> tuple:
        pass

    def _calculates_buy_and_sell_data(self, link_end: str, answer: dict
                                      ) -> tuple[dict, dict]:
        buy_price, sell_price = self._extract_buy_and_sell_from_json(answer,
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

    def _add_to_bulk_update_or_create(self, value_dict: dict) -> None:
        bank_names = []
        for name, value in self.banks_config.items():
            if self.currency_markets_name in value['bank_invest_exchanges']:
                bank_names.append(name)
        for bank_name in bank_names:
            bank = Banks.objects.get(name=bank_name)
            price = value_dict['price']
            target_object = self.model.objects.filter(
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
                created_object = self.model(
                    bank=bank,
                    currency_market=self.currency_market,
                    from_fiat=value_dict['from_fiat'],
                    to_fiat=value_dict['to_fiat'],
                    price=price,
                    update=self.new_update
                )
                self.records_to_create.append(created_object)

    def _get_all_api_answers(self) -> None:
        for link_end in self.link_ends:
            answer = self._get_api_answer(link_end)
            if answer is False:
                continue
            buy_and_sell_data = self._calculates_buy_and_sell_data(link_end,
                                                                   answer)
            for buy_or_sell_data in buy_and_sell_data:
                self._add_to_bulk_update_or_create(buy_or_sell_data)


class P2PParser(CryptoParser, ABC):
    model = P2PCryptoExchangesRates
    model_update = P2PCryptoExchangesRatesUpdates
    updated_fields = ['price', 'update']
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
        self.trade_types = self.crypto_exchanges_configs.get('trade_types')
        self.banks_configs = self.banks_config[self.bank_name]
        self.fiats = set(self.banks_configs['currencies'])
        self.if_no_objects = self.model.objects.filter(
            payment_channel=self.payment_channel).count() == 0
        self.if_new_hour = datetime.now(
            timezone.utc
        ).time().hour != self.model_update.objects.last().updated.time().hour
        self.full_update = self.if_no_objects or self.if_new_hour

    @abstractmethod
    def _create_body(self, asset: str, trade_type: str, fiat: str) -> dict:
        pass

    @staticmethod
    @abstractmethod
    def _extract_price_from_json(json_data: dict) -> float | None | bool:
        pass

    def _get_api_answer(self, asset: str, trade_type: str, fiat: str) -> dict:
        body = self._create_body(asset, trade_type, fiat)
        headers = self._create_headers(body)
        return self._get_api_answer_post(body, headers)

    def _add_to_bulk_update_or_create(self, asset: str, trade_type: str,
                                      fiat: str, price: float) -> None:
        target_object = self.model.objects.filter(
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
            created_object = self.model(
                crypto_exchange=self.crypto_exchange, asset=asset,
                trade_type=trade_type, fiat=fiat, bank=self.bank,
                price=price, update=self.new_update,
                payment_channel=self.payment_channel
            )
            self.records_to_create.append(created_object)

    def _get_all_api_answers(self) -> None:
        for fiat in self.fiats:
            assets = self.crypto_exchanges_configs['assets_for_fiats'].get(fiat
                                                                           )
            if not assets:
                assets = self.crypto_exchanges_configs['assets_for_fiats'
                                                       ]['all']
            for trade_type, asset in product(self.trade_types, set(assets)):
                if not self.full_update:
                    target_rates = self.model.objects.filter(
                        crypto_exchange=self.crypto_exchange,
                        asset=asset, trade_type=trade_type, fiat=fiat,
                        bank=self.bank, payment_channel=self.payment_channel
                    )
                    if target_rates.exists() and not target_rates.get().price:
                        continue
                response = self._get_api_answer(asset, fiat, trade_type)
                if response is False:
                    continue
                price = self._extract_price_from_json(response)
                if price is not None:
                    price = 1 / price if trade_type == 'BUY' else price
                self._add_to_bulk_update_or_create(
                    asset, trade_type, fiat, price
                )


class CryptoExchangesParser(BaseParser, ABC):
    model = IntraCryptoExchanges
    model_update = IntraCryptoExchangesUpdates
    updated_fields = ['price', 'update']
    crypto_exchange_name: str
    name_from: str
    exceptions: tuple[str]
    CURRENCY_PAIR = 2

    def __init__(self) -> None:
        super().__init__()
        from crypto_exchanges.crypto_exchanges_config import (
            CRYPTO_EXCHANGES_CONFIG)
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
    def _create_params(self, fiats_combinations: tuple) -> list[dict[str]]:
        pass

    @abstractmethod
    def _get_api_answer(self, params: dict) -> dict:
        pass

    @staticmethod
    @abstractmethod
    def _extract_price_from_json(json_data: dict) -> float:
        pass

    @abstractmethod
    def _calculates_buy_and_sell_data(self, params
                                      ) -> tuple[dict, dict] | None:
        pass

    def _generate_unique_params(self) -> list[dict[str]]:
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
        return self._create_params(currencies_combinations)

    def _add_to_bulk_update_or_create(self, value_dict: dict, price: float
                                      ) -> None:
        target_object = self.model.objects.filter(
            crypto_exchange=self.crypto_exchange,
            from_asset=value_dict['from_asset'],
            to_asset=value_dict['to_asset']
        )
        if target_object.exists():
            updated_object = self.model.objects.get(
                crypto_exchange=self.crypto_exchange,
                from_asset=value_dict['from_asset'],
                to_asset=value_dict['to_asset']
            )
            updated_object.price = price
            updated_object.update = self.new_update
            self.records_to_update.append(updated_object)
        else:
            created_object = self.model(
                crypto_exchange=self.crypto_exchange,
                from_asset=value_dict['from_asset'],
                to_asset=value_dict['to_asset'],
                price=price, spot_fee=value_dict['spot_fee'],
                update=self.new_update
            )
            self.records_to_create.append(created_object)

    def _get_all_api_answers(self) -> None:
        unique_params = self._generate_unique_params()
        for params in unique_params:
            values = self._calculates_buy_and_sell_data(params)
            if values is None:
                continue
            for value_dict in values:
                price = value_dict.pop('price')
                self._add_to_bulk_update_or_create(value_dict, price)


class ListsFiatCryptoParser(CryptoParser, ABC):
    model = ListsFiatCrypto
    model_update = ListsFiatCryptoUpdates
    updated_fields = ['list_fiat_crypto', 'update']
    crypto_exchange_name: str
    endpoint_sell: str
    endpoint_buy: str

    def __init__(self) -> None:
        super().__init__()
        self.new_update = self.model_update.objects.create(
            crypto_exchange=self.crypto_exchange
        )

    @staticmethod
    def _create_body_sell(asset: str) -> dict:
        pass

    @staticmethod
    def _create_body_buy(fiat: str) -> dict:
        pass

    def _extract_buy_or_sell_list_from_json(self, json_data: dict,
                                            trade_type: str) -> List[list]:
        pass

    def _get_api_answer(self, asset=None, fiat=None) -> dict:
        if asset:
            body = self.create_body_sell(asset)
            endpoint = self.endpoint_sell
        else:  # if fiat
            body = self._create_body_buy(fiat)
            endpoint = self.endpoint_buy
        headers = self._create_headers(body)
        return self._get_api_answer_post(body, headers, endpoint=endpoint)

    def _add_to_update_or_create(self, list_fiat_crypto: dict, trade_type: str
                                 ) -> None:
        target_object = self.model.objects.filter(
            crypto_exchange=self.crypto_exchange, trade_type=trade_type
        )
        if target_object.exists():
            updated_object = self.model.objects.get(
                crypto_exchange=self.crypto_exchange, trade_type=trade_type
            )
            updated_object.list_fiat_crypto = list_fiat_crypto
            updated_object.update = self.new_update
            self.records_to_update.append(updated_object)
        else:
            created_object = self.model(
                crypto_exchange=self.crypto_exchange,
                list_fiat_crypto=list_fiat_crypto,
                trade_type=trade_type,
                update=self.new_update
            )
            self.records_to_create.append(created_object)

    def _get_all_api_answers(self) -> None:
        sell_dict = {}
        for asset in self.assets:
            response_sell = self._get_api_answer(asset=asset)
            if response_sell is False:
                continue
            sell_list = self.extract_buy_or_sell_list_from_json(response_sell,
                                                                'SELL')
            sell_dict[asset] = sell_list

        buy_dict = {}
        for fiat in self.all_fiats:
            response_buy = self._get_api_answer(fiat=fiat)
            if response_buy is False:
                continue
            buy_list = self._extract_buy_or_sell_list_from_json(response_buy,
                                                                'BUY')
            for asset_info in buy_list:
                fiat_list = []
                if asset_info[0] not in buy_dict:
                    buy_dict[asset_info[0]] = fiat_list
                buy_dict[asset_info[0]].append([fiat, asset_info[1]])

        self.add_to_update_or_create(sell_dict, trade_type='SELL')
        self.add_to_update_or_create(buy_dict, trade_type='BUY')


class Card2CryptoExchangesParser(CryptoParser, ABC):
    model = P2PCryptoExchangesRates
    model_update = P2PCryptoExchangesRatesUpdates
    payment_channel = 'Card2CryptoExchange'
    transaction_method = 'Bank Card (Visa/MC)'
    updated_fields = ['price', 'pre_price', 'transaction_fee', 'update']
    endpoint_sell: str
    endpoint_buy: str

    def __init__(self, trade_type: str) -> None:
        super().__init__()
        self.new_update = self.model_update.objects.create(
            crypto_exchange=self.crypto_exchange,
            payment_channel=self.payment_channel
        )
        self.trade_type = trade_type
        self.if_no_objects = self.model.objects.filter(
            payment_channel=self.payment_channel).count() == 0
        self.if_new_hour = datetime.now(
            timezone.utc
        ).time().hour != self.model_update.objects.last().updated.time().hour
        self.full_update = self.if_no_objects or self.if_new_hour

    @staticmethod
    def _create_body_sell(fiat: str, asset: str, amount: int) -> dict:
        pass

    @staticmethod
    def _create_body_buy(fiat: str, asset: str, amount: int) -> dict:
        pass

    @staticmethod
    def _create_params_buy(fiat: str, asset: str) -> dict:
        pass

    def _extract_values_from_json(self, json_data: dict, amount: int
                                  ) -> tuple | None:
        pass

    def _get_api_answer(self, asset: str, fiat: str, amount: int) -> dict:
        if self.trade_type == 'SELL':
            body = self._create_body_sell(fiat, asset, amount)
            headers = self._create_headers(body)
            return self._get_api_answer_post(
                body, headers, endpoint=self.endpoint_sell
            )
        params = self._create_params_buy(fiat, asset)
        return self._get_api_answer_get(params, endpoint=self.endpoint_buy)

    def __check_p2p_exchange_is_better(self, asset: str, fiat: str,
                                       price: float, bank: Banks) -> bool:
        p2p_exchange = self.model.objects.filter(
            crypto_exchange=self.crypto_exchange, bank=bank,
            asset=asset,
            trade_type=self.trade_type, fiat=fiat,
            payment_channel='P2P', price__isnull=False
        )
        if p2p_exchange.exists():
            p2p_price = p2p_exchange.get().price
            if_bad_buy_price = (
                self.trade_type == 'BUY' and price > p2p_price)
            if_bad_sell_price = (
                self.trade_type == 'SELL' and price < p2p_price)
            if if_bad_buy_price or if_bad_sell_price:
                return True
        return False

    def _add_to_bulk_update_or_create(self, asset: str, fiat: str,
                                      price: float, pre_price: float,
                                      transaction_fee: float) -> None:
        bank_names = []
        for name, value in self.banks_config.items():
            if self.payment_channel in value['payment_channels']:
                bank_names.append(name)
        for bank_name in bank_names:
            bank = Banks.objects.get(name=bank_name)
            target_object = self.model.objects.filter(
                crypto_exchange=self.crypto_exchange, bank=bank, asset=asset,
                trade_type=self.trade_type, fiat=fiat,
                transaction_method=self.transaction_method,
                payment_channel=self.payment_channel
            )
            if self.__check_p2p_exchange_is_better(asset, fiat, price, bank):
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
                created_object = self.model(
                    crypto_exchange=self.crypto_exchange, bank=bank,
                    asset=asset, trade_type=self.trade_type, fiat=fiat,
                    price=price, pre_price=pre_price,
                    transaction_fee=transaction_fee, update=self.new_update,
                    payment_channel=self.payment_channel,
                    transaction_method=self.transaction_method,
                )
                self.records_to_create.append(created_object)

    def _get_all_api_answers(self) -> None:
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
                    target_rates = self.model.objects.filter(
                        crypto_exchange=self.crypto_exchange, asset=asset,
                        trade_type=self.trade_type, fiat=fiat,
                        payment_channel=self.payment_channel
                    )
                    if not target_rates.exists():
                        continue
                response = self._get_api_answer(asset, fiat, amount)
                if response is None:
                    continue
                values = self._extract_values_from_json(response, amount)
                if values is None:
                    continue
                price, pre_price, commission = values
                self._add_to_bulk_update_or_create(
                    asset, fiat, price, pre_price, commission
                )
