from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from itertools import combinations, permutations, product
from sys import getsizeof
from typing import Any, Dict, List, Optional

import requests

from arbitration.settings import DATA_OBSOLETE_IN_MINUTES
from banks.models import (Banks, BanksExchangeRates, BanksExchangeRatesUpdates,
                          CurrencyMarkets)
from core.loggers import ParsingLogger
from core.tor import Tor
from crypto_exchanges.models import (CryptoExchanges, CryptoExchangesRates,
                                     CryptoExchangesRatesUpdates,
                                     IntraCryptoExchangesRates,
                                     IntraCryptoExchangesRatesUpdates,
                                     ListsFiatCrypto, ListsFiatCryptoUpdates)


class BaseParser(ParsingLogger, ABC):
    """
    Base class for all parsers. Inherits from ParsingLogger and ABC classes.

    Attributes:
        endpoint (str):  API endpoint URL
        updated_fields (List[str]):  List of fields to update
        bank_name (str): Placeholder for the bank name
        CURRENCY_PAIR: Representing the number of currencies to combine.
    """
    endpoint: str
    updated_fields: List[str]
    bank_name = None
    CURRENCY_PAIR: int = 2

    def __init__(self) -> None:
        from banks.banks_config import BANKS_CONFIG
        super().__init__()
        self.records_to_update = []
        self.records_to_create = []
        self.banks_config = BANKS_CONFIG

    def _get_count_created_objects(self) -> None:
        """
        Sets the count of created objects to the count of records to create.
        """
        self.count_created_objects = len(self.records_to_create)

    def _get_count_updated_objects(self) -> None:
        """
        Sets the count of updated objects to the count of records to update.
        """
        self.count_updated_objects = len(self.records_to_update)

    def _successful_response_handler(self) -> None:
        """
        Logs a message when a response is successfully handled.
        """
        message = (f'Successful response with class: '
                   f'{self.__class__.__name__}')
        self.logger.info(message)

    def _unsuccessful_response_handler(self, error: Exception) -> None:
        """
        Logs an error message when a response cannot be handled.
        """
        message = (f'{error} with response, class: '
                   f'{self.__class__.__name__}.')
        self.logger.error(message)

    def _negative_response_status_handler(self, response: requests.Response
                                          ) -> None:
        """
        Logs an error message when the response status code is not OK.
        """
        message = (f'{response.status_code} with response, class: '
                   f'{self.__class__.__name__}.')
        self.logger.error(message)

    @abstractmethod
    def _get_all_api_answers(self) -> None:
        """
        This abstract method is the nodal method in all parsers. It should
        enumerate all the necessary combinations for API requests and call
        auxiliary methods. All logic is implemented in separate methods.
        """
        pass

    def main(self) -> None:
        """
        This method is the main method of the class and is responsible for
        running the entire process. It calls the _get_all_api_answers method to
        generate the data, then bulk creates or updates the records in the
        model. After that, it calculates the duration of the process and saves
        it to the database. If an error occurs during the process, it logs the
        error and raises an exception.
        """
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
    """
    Class for parsers that use the Tor network. Inherits from BaseParser and
    ABC classes.

    Attributes:
        LIMIT_TRY (int): Maximum number of tries to make a request
        tor (Tor): Tor object for making requests
        count_try (int): Current count of tries
    """
    LIMIT_TRY = 3

    def __init__(self) -> None:
        super().__init__()
        self.tor = Tor()
        self.count_try = 0

    def _get_api_answer_post(self, body: dict, headers: dict, endpoint=None
                             ) -> dict | bool:
        """
        Sends a POST request to the specified API endpoint and returns
        the response.
        """
        self.count_try = 0
        if endpoint is None:
            endpoint = self.endpoint
        while self.count_try < self.LIMIT_TRY:
            try:
                response = self.tor.session.post(
                    endpoint, headers=headers, json=body
                )
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
        """
        Sends a GET request to the specified API endpoint and returns
        the response.
        """
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

    def _unsuccessful_response_handler(self, error: Exception) -> None:
        """
        Logs an error message when a response cannot be handled.
        """
        message = (f'{error} with response, class: '
                   f'{self.__class__.__name__}, count try: {self.count_try}')
        self.logger.error(message)
        self.tor.renew_connection()
        self.count_try += 1

    def _negative_response_status_handler(self, response: requests.Response
                                          ) -> None:
        """
        Logs an error message when the response status code is not OK.
        """
        message = (f'{response.status_code} with response, class: '
                   f'{self.__class__.__name__}, count try: {self.count_try}')
        self.logger.error(message)
        self.tor.renew_connection()
        self.count_try += 1


class CryptoParser(ParsingViaTor, ABC):
    """
    This class is a subclass of ParsingViaTor and ABC. It parses crypto
    exchange data from API, creates the headers and gets the required assets.

    Attributes:
        crypto_exchange_name (str): Representing the name of the crypto
            exchange.
        crypto_exchanges_configs (dict): Dictionary with the configurations of
            the crypto exchange.
        assets (set): Representing the assets to parse.
        all_fiats (set): Representing all fiat currencies.
        crypto_exchange: An object representing the CryptoExchanges model.
    """
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
        """
        A static method that takes the request body as a parameter and returns
        a header with the calculated content length.
        """
        return {
            'Content-Type': 'application/json',
            'Content-Length': str(getsizeof(body))
        }


class BankParser(ParsingViaTor, ABC):
    """
    This class is a subclass of ParsingViaTor and ABC. It parses bank exchange
    rates data from API, calculates the buy and sell data or the price data,
    and updates the database.

    Attributes:
        model: The Django model representing the bank exchange rates.
        model_update: The Django model representing the updates of the bank
            exchange rates.
        updated_fields (list): A list of strings representing the
            fields to update in the model.
        bank_name (str): Representing the name of the bank.
        buy_and_sell (bool): Indicating whether the API should return buy
            and sell data or not.
        all_values (bool): Indicating whether the API should return all
            values or not.
        name_from (str): Representing the name of the currency key to buy.
        name_to (str): Representing the name of the currency key to sell.
    """
    model = BanksExchangeRates
    model_update = BanksExchangeRatesUpdates
    updated_fields: List[str] = ['price', 'update']
    bank_name: str
    buy_and_sell: bool
    all_values: bool = False
    name_from: str
    name_to: str

    def __init__(self) -> None:
        super().__init__()
        self.bank = Banks.objects.get(name=self.bank_name)
        self.new_update = self.model_update.objects.create(bank=self.bank)

    def _create_params(self, fiats_combinations: tuple) -> list[dict[str]]:
        """
        Abstract method that should be implemented by a subclass to create a
        list of parameters to send to the API.
        """
        pass

    def _generate_unique_params(self) -> list[dict[str]]:
        """
        Generates a list of unique parameters to send to the API.
        """
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
        """
        Abstract method that should be implemented by a subclass to extract
        buy and sell data from the API response.
        """
        pass

    def _extract_price_from_json(self, json_data: dict) -> float:
        """
        Abstract method that should be implemented by a subclass to extract
        price data from the API response.
        """
        pass

    def _extract_all_values_from_json(self, json_data: dict
                                      ) -> Optional[List[Dict[str, Any]]]:
        """
        Abstract method that should be implemented by a subclass to extracts
        all values data from the API response.
        """
        pass

    def _calculates_buy_and_sell_data(self, params: dict) -> tuple[dict, dict]:
        """
        Calculates the buy and sell data for a given set of
        parameters. It gets the API response using the _get_api_answer_get
        method, extracts the buy and sell data using the
        _extract_buy_and_sell_from_json method, and returns a tuple of
        dictionaries containing the calculated buy and sell data.
        """
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
        """
        Calculates the price data for a given set of parameters.
        It gets the API response using the _get_api_answer_get method, extracts
        the price data using the _extract_price_from_json method, and returns a
        list of dictionaries containing the calculated price data.
        """
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
        """
        Calculates all values data. It gets the API response using the
        _get_api_answer_get method, extracts all values data using the
        _extract_all_values_from_json method, and returns a list of
        dictionaries containing the calculated data, or None if no data is
        available.
        """
        response_json = self._get_api_answer_get()
        return self._extract_all_values_from_json(response_json)

    def _choice_buy_and_sell_or_price(self, params=None
                                      ) -> tuple[dict, dict] | list[dict]:
        """
        Chooses whether to calculate buy and sell data, price data, or all
        values data, depending on the buy_and_sell and all_values attributes.
        It calls the appropriate calculation method and returns the calculated
        data.
        """
        if self.all_values:
            return self._calculates_all_values_data()
        if self.buy_and_sell:
            return self._calculates_buy_and_sell_data(params)
        return self._calculates_price_data(params)

    def _add_to_bulk_update_or_create(self, value_dict: dict, price: float
                                      ) -> None:
        """
        Adds a record to the list of records to update or create. It checks if
        a record with the same parameters already exists in the database, and
        updates it with the new price and update record, or creates a new
        record if it does not exist.
        """
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
                if price is None:
                    continue
                self._add_to_bulk_update_or_create(value_dict, price)


class BankInvestParser(ParsingViaTor, ABC):
    """
    This class parses exchange rates data from Bank Invest website and stores
    it in the database. It inherits from `ParsingViaTor` and `ABC`.

    Attributes:
        model: The Django model to use for creating or updating exchange rates
            data.
        model_update: The Django model to use for creating update objects.
        updated_fields (list): The fields to update when updating exchange
            rates data.
        currency_markets_name (str): The name of the currency market to use
            when creating or updating exchange rates data.
        link_ends (str): The string of link ends to use when constructing the
            URLs to make requests to the Bank Invest API.
    """
    model = BanksExchangeRates
    model_update = BanksExchangeRatesUpdates
    updated_fields: List[str] = ['price', 'update']
    currency_markets_name: str
    link_ends: str

    def __init__(self) -> None:
        super().__init__()
        self.currency_market = CurrencyMarkets.objects.get(
            name=self.currency_markets_name)
        self.new_update = self.model_update.objects.create(
            currency_market=self.currency_market
        )

    def _get_api_answer(self, link_end: str) -> dict:
        """
        Makes a GET request to the Bank Invest API and returns the response
        data as a dictionary.
        """
        endpoint = self.endpoint + link_end
        return self._get_api_answer_get(endpoint=endpoint)

    @staticmethod
    @abstractmethod
    def _extract_buy_and_sell_from_json(json_data: dict, link_end: str
                                        ) -> tuple:
        """
        Abstract method to extract buy and sell prices from the JSON data
        returned by the Bank Invest API.
        """
        pass

    def _calculates_buy_and_sell_data(self, link_end: str, answer: dict
                                      ) -> tuple[dict, dict]:
        """
        Calculates the buy and sell data based on the API answer.
        """
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
        """
        Adds the given data dictionary to the bulk update list or bulk
        create list depending on whether the object already exists.
        """
        bank_names = []
        for name, value in self.banks_config.items():
            if self.currency_markets_name in value['bank_invest_exchanges']:
                bank_names.append(name)
        for bank_name in bank_names:
            bank = Banks.objects.get(name=bank_name)
            target_object = self.model.objects.filter(
                bank=bank,
                currency_market=self.currency_market,
                from_fiat=value_dict['from_fiat'],
                to_fiat=value_dict['to_fiat']
            )
            if target_object.exists():
                updated_object = target_object.get()
                updated_object.price = value_dict['price']
                updated_object.update = self.new_update
                self.records_to_update.append(updated_object)
            else:
                created_object = self.model(
                    bank=bank,
                    currency_market=self.currency_market,
                    from_fiat=value_dict['from_fiat'],
                    to_fiat=value_dict['to_fiat'],
                    price=value_dict['price'],
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
    """
    This class is a subclass of the CryptoParser class and represents a parser
    for peer-to-peer exchanges rates. It has the following attributes.

    Attributes:
        model: A Django model representing the exchange rates to be parsed.
        model_update: A Django model representing the updates to be made to
            the exchange rates.
        updated_fields (list): A list of fields to be updated in the model
            when new exchange rates are fetched.
        bank_name (str): Representing the name of the bank to be parsed.
        page (int): Representing the page number to be parsed.
        rows (int): Representing the number of rows to be parsed.
        payment_channel: A string representing the payment channel for which
            the exchange rates are to be fetched.
    """
    model = CryptoExchangesRates
    model_update = CryptoExchangesRatesUpdates
    updated_fields: List[str] = ['price', 'update']
    bank_name: str
    page: int
    rows: int
    payment_channel: str = 'P2P'

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
        ).time().minute < self.model_update.objects.last().updated.time(
        ).minute
        self.full_update = self.if_no_objects or self.if_new_hour

    @abstractmethod
    def _create_body(self, asset: str, trade_type: str, fiat: str) -> dict:
        """
        An abstract method that creates the request body for fetching exchange
        rates.
        """
        pass

    @staticmethod
    @abstractmethod
    def _extract_price_from_json(json_data: dict) -> float | None | bool:
        """
        An abstract method that extracts the exchange rate from the JSON
        response.
        """
        pass

    def _get_api_answer(self, asset: str, trade_type: str, fiat: str) -> dict:
        """
        Fetches the API response for a given asset, trade type, and fiat.
        """
        body = self._create_body(asset, trade_type, fiat)
        headers = self._create_headers(body)
        return self._get_api_answer_post(body, headers)

    def _add_to_bulk_update_or_create(self, asset: str, trade_type: str,
                                      fiat: str, price: float) -> None:
        """
        Adds the exchange rate to be bulk updated or created.
        """
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
    """
    A base parser class for extracting intra-exchange cryptocurrency rates data
    from different cryptocurrency exchanges.

    Attributes:
        model: A Django model representing the exchange rates to be parsed.
        model_update: A Django model representing the updates to be made to
            the exchange rates.
        updated_fields (list): A list of fields to be updated in the model
            when new exchange rates are fetched.
        crypto_exchange_name (str): Representing the name of the crypto
            exchange.
        name_from (str): Representing the name of the params key.
    """
    model = IntraCryptoExchangesRates
    model_update = IntraCryptoExchangesRatesUpdates
    updated_fields: List[str] = ['price', 'update']
    crypto_exchange_name: str
    name_from: str

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
        """
        Abstract method that creates parameters for the cryptocurrency exchange
        API endpoint.
        """
        pass

    @abstractmethod
    def _get_api_answer(self, params: dict) -> dict:
        """
        Abstract method that sends a request to the cryptocurrency exchange API
        endpoint and returns the response.
        """
        pass

    @staticmethod
    @abstractmethod
    def _extract_price_from_json(json_data: dict) -> float:
        """
        Abstract method that extracts the price data from the cryptocurrency
        exchange API response.
        """
        pass

    @abstractmethod
    def _calculates_buy_and_sell_data(self, params
                                      ) -> tuple[dict, dict] | None:
        """
        Abstract method that calculates the buy and sell data for each
        cryptocurrency asset pair.
        """
        pass

    def _generate_unique_params(self) -> list[dict[str]]:
        """
        Method that generates unique parameters for the cryptocurrency exchange
        API endpoint.
        """
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
        """
        Adds the given data dictionary to the bulk update list or bulk
        create list depending on whether the object already exists.
        """
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
    """
    This class is a subclass of CryptoParser abstract class. Represents a
    parser for parsing exchange rates from a specific API. The exchange rates
    are related to the list of fiat and cryptocurrencies supported by a
    specific exchange.

    Attributes:
        model: A Django model representing the exchange rates to be parsed.
        model_update: A Django model representing the updates to be made to
            the exchange rates.
        updated_fields (list): A list of fields to be updated in the model
            when new exchange rates are fetched.
        endpoint_sell (str): the API endpoint for fetching the sell rates.
        endpoint_buy (str): the API endpoint for fetching the buy rates.
    """
    model = ListsFiatCrypto
    model_update = ListsFiatCryptoUpdates
    updated_fields: List[str] = ['list_fiat_crypto', 'update']
    endpoint_sell: str
    endpoint_buy: str

    def __init__(self) -> None:
        super().__init__()
        self.new_update = self.model_update.objects.create(
            crypto_exchange=self.crypto_exchange
        )

    @staticmethod
    def _create_body_sell(asset: str) -> dict:
        """
        A static method that creates the request body for fetching sell rates
        for a specific asset.
        """
        pass

    @staticmethod
    def _create_body_buy(fiat: str) -> dict:
        """
        A static method that creates the request body for fetching buy rates
        for a specific fiat.
        """
        pass

    @abstractmethod
    def _extract_buy_or_sell_list_from_json(self, json_data: dict,
                                            trade_type: str) -> List[list]:
        """
        A method that extracts the relevant data from the JSON response
        returned by the API.
        """
        pass

    def _get_api_answer(self, asset=None, fiat=None) -> dict:
        """
        A method that makes a request to the API to fetch either the sell or
        buy rates, depending on the input parameters.
        """
        if asset:
            body = self._create_body_sell(asset)
            endpoint = self.endpoint_sell
        else:  # if fiat
            body = self._create_body_buy(fiat)
            endpoint = self.endpoint_buy
        headers = self._create_headers(body)
        return self._get_api_answer_post(body, headers, endpoint=endpoint)

    def _add_to_update_or_create(self, list_fiat_crypto: dict, trade_type: str
                                 ) -> None:
        """
        A method that adds the fetched data to the update model or creates a
        new entry in the model, depending on whether the data for the
        specific exchange already exists.
        """
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
            sell_list = self._extract_buy_or_sell_list_from_json(response_sell,
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

        self._add_to_update_or_create(sell_dict, trade_type='SELL')
        self._add_to_update_or_create(buy_dict, trade_type='BUY')


class Card2CryptoExchangesParser(CryptoParser, ABC):
    """
    This class is derived from CryptoParser class and inherits all of its
    attributes and methods. The purpose of this class is to parse exchange
    rates from a Card to Crypto exchange.

    Attributes:
        model: A Django model representing the exchange rates to be parsed.
        model_update: A Django model representing the updates to be made to
            the exchange rates.
        transaction_method (str): Representing the transaction method used in
            the exchange.
        updated_fields (list): A list of fields to be updated in the model
            when new exchange rates are fetched.
        endpoint_sell (str): Representing the endpoint for selling
            cryptocurrency.
        endpoint_buy (str): Representing the endpoint for buying
            cryptocurrency.
        data_obsolete_in_minutes (int): The time in minutes since the last
            update, after which the data is considered out of date and does not
            participate in calculations.
    """
    model = CryptoExchangesRates
    model_update = CryptoExchangesRatesUpdates
    payment_channel: str = 'Card2CryptoExchange'
    transaction_method: str = 'Bank Card (Visa/MC)'
    updated_fields: List[str] = [
        'price', 'pre_price', 'transaction_fee', 'update'
    ]
    endpoint_sell: str
    endpoint_buy: str
    data_obsolete_in_minutes: int = DATA_OBSOLETE_IN_MINUTES

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
        ).time().minute < self.model_update.objects.last().updated.time(
        ).minute
        self.full_update = self.if_no_objects or self.if_new_hour
        self.update_time = datetime.now(timezone.utc) - timedelta(
            minutes=self.data_obsolete_in_minutes
        )

    @staticmethod
    def _create_body_sell(fiat: str, asset: str, amount: int) -> dict:
        """
        Creates a dictionary representing the request body for selling
        cryptocurrency.
        """
        pass

    @staticmethod
    def _create_body_buy(fiat: str, asset: str, amount: int) -> dict:
        """
        Creates a dictionary representing the request body for buying
        cryptocurrency.
        """
        pass

    @staticmethod
    def _create_params_buy(fiat: str, asset: str) -> dict:
        """
        Creates a dictionary representing the query parameters for buying
        cryptocurrency.
        """
        pass

    @abstractmethod
    def _extract_values_from_json(self, json_data: dict, amount: int
                                  ) -> tuple | None:
        """
        Extracts values from the JSON response and returns a tuple of values.
        """
        pass

    def _get_api_answer(self, asset: str, fiat: str, amount: int) -> dict:
        """
        Returns the API response for a given asset, fiat and amount.
        """
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
        """
        Checks if a P2P exchange offers a better price than the current
        exchange.
        """
        p2p_exchange = self.model.objects.select_related('update').filter(
            crypto_exchange=self.crypto_exchange, bank=bank, asset=asset,
            trade_type=self.trade_type, fiat=fiat, payment_channel='P2P',
            price__isnull=False, update__updated__gte=self.update_time
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
        """
        Updates or creates an exchange rate object in the database based on the
        given parameters.
        """
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
