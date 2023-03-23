from __future__ import annotations

import json
import random
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from itertools import combinations, permutations, product
from typing import Any, Dict, List, Optional, Tuple, Union

import requests
from fake_useragent import UserAgent

from arbitration.settings import DATA_OBSOLETE_IN_MINUTES
from banks.models import (Banks, BanksExchangeRates, BanksExchangeRatesUpdates,
                          CurrencyMarkets)
from core.connection_types.direct import Direct
from core.connection_types.proxy import Proxy
from core.connection_types.tor import Tor
from core.cookie import Cookie
from core.loggers import ParsingLogger
from crypto_exchanges.models import (CryptoExchanges, CryptoExchangesRates,
                                     CryptoExchangesRatesUpdates,
                                     IntraCryptoExchangesRates,
                                     IntraCryptoExchangesRatesUpdates,
                                     ListsFiatCrypto, ListsFiatCryptoUpdates)


class BaseParser(ParsingLogger, ABC):
    """
    This is the base class for all parsers. BaseParser inherits from
    ParsingLogger and is an abstract class. It allows you to make requests to
    the API through the Tor network, Proxy or directly. Child classes can be
    flexibly configured through its public interfaces.

    Attributes:
        endpoint (str):  API endpoint URL
        updated_fields (List[str]):  List of fields to update
        bank_name (str): Placeholder for the bank name
        connection_type (str): The type of the connection. Either Tor, Proxy
            or Direct.
        request_method (str): The type of the request method. POST or GET.
        need_cookies (bool): A boolean indicating if cookies are needed.
        cookies_names (Tuple[str]): A tuple of cookie names.
        cookie_spoiled (bool): A boolean indicating if the cookie is corrupted.
        user_agent_spoiled (bool): A boolean indicating if the user agent is
            corrupted.
        headers (Dict[str, Any]): A dictionary containing the headers.
        custom_user_agent (Tuple[str]): A tuple of custom user agent strings.
        user_agent_browser (str): The browser to use for fake user agent.
        waiting_time (int): The amount of time to wait.
        fake_useragent (bool): A boolean indicating if a fake user agent is
            needed.
        content_type (str): The content type.
        request_timeout (int): The request timeout.
        connection_start_time (datetime): Time to start connecting to the API.

        LIMIT_TRY (int): Maximum number of tries to make a request.
        CURRENCY_PAIR: Representing the number of currencies to combine.
    """
    endpoint: str
    updated_fields: List[str]
    bank_name: str = None
    connection_type: str
    request_method: str = None
    need_cookies: bool
    cookies_names: Tuple[str] = None
    cookie_spoiled: bool = True
    user_agent_spoiled: bool = True
    headers: Dict[str, Any] = None
    custom_user_agent: Tuple[str] = [None]
    user_agent_browser: str = 'chrome'
    waiting_time: int = 0
    fake_useragent: bool = True
    content_type: str = 'application/json'
    request_timeout: int = None
    connection_start_time: datetime
    LIMIT_TRY: int = 3
    CURRENCY_PAIR: int = 2

    def __init__(self) -> None:
        super().__init__()
        from banks.banks_config import BANKS_CONFIG
        self.records_to_update = []
        self.records_to_create = []
        self.first_request = True
        self.banks_config = BANKS_CONFIG
        self.connection = self.__choose_connection_type()
        self.cookie = Cookie(
            self.endpoint, self.connection.session, self.cookies_names
        ) if self.need_cookies else None
        self.user_agent = UserAgent()
        self.count_try = 0
        self.request_value = {}

    def __choose_connection_type(self) -> Union[Tor, Proxy, Direct]:
        """
        This private method creates an instance of the class to connect to the
        request session via: Tor network or Proxy or Direct, depending on the
        connection_type setting declared in the child class.
        """
        self.connection_type.capitalize()
        if self.connection_type == 'Tor':
            return Tor()
        if self.connection_type == 'Proxy':
            return Proxy()
        if self.connection_type == 'Direct':
            return Direct()
        raise ValueError(f'Invalid connection type: {self.connection_type}')

    def __choose_request_method(self, body=None, params=None) -> str:
        """
        This private method returns the HTTP string name of the request,
        depending on the request_method setting in the child class or the
        passed body or params declared.
        """
        if self.request_method is not None:
            return self.request_method
        if body is None:
            return 'get'
        if body is not None and params is None:
            return 'post'
        raise ValueError(
            f'Invalid request method: body: {body}, params{params}')

    def __create_request_value(self, body: dict, params: dict) -> None:
        """
        This private method creates a dictionary of values, based on the passed
        body or params, to be sent by the HTTP method via an instance of the
        requests.sessions.Session class.
        """
        self.request_value = {
            'timeout': self.request_timeout or self.connection.request_timeout
        }
        if self.request_method == 'get' or body is None:
            self.request_value['params'] = params
        else:
            self.request_value['json'] = body

    def __create_cookies(self) -> None:
        """
        This private method creates an instance of the Cookie class and uses
        its add_cookies_to_headers method to add them to the current request
        headers. And marks cookies as relevant.
        """
        Cookie(
            self.endpoint, self.connection.session, self.cookies_names
        ).add_cookies_to_headers()
        self.cookie_spoiled = False

    def __give_more_tries_if_first_request(self) -> None:
        """
        This private method adds two additional retries for the first
        connection to the API if the connection is made through the Tor network
        or Proxy.
        """
        if self.first_request and self.connection_type.upper() != 'Direct':
            self.count_try = -2
            self.first_request = False
        else:
            self.count_try = 0

    def __start_request_handler(self, body=None, params=None) -> None:
        """
        This private method runs all the methods required before sending the
        API request so as not to overload the _send_request method.
        """
        self.__give_more_tries_if_first_request()
        self._create_headers(body)
        self.__create_request_value(body, params)
        self.connection_start_time = datetime.now(timezone.utc)
        if self.need_cookies and self.cookie_spoiled:
            self.__create_cookies()

    def __renew_connection(self, body: dict | None) -> None:
        """
        This private method runs all the necessary methods to renew connect.
        """
        start_time_renew_connection = datetime.now(timezone.utc)
        self.connection.renew_connection()
        renew_connections_duration = (
            datetime.now(timezone.utc) - start_time_renew_connection
        ).seconds
        self.renew_connections_duration += round(
            renew_connections_duration, 2)
        self._create_headers(body)
        self.cookie_spoiled = True
        self.user_agent_spoiled = True
        self.count_try += 1

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

    def _send_request(self, body=None, params=None) -> dict | bool:
        """
        Sends request with any methods to the specified API endpoint and
        returns the response or False.
        """
        self.__start_request_handler(body, params)
        while self.count_try < self.LIMIT_TRY:
            try:
                response = getattr(
                    self.connection.session,
                    self.__choose_request_method(body=body, params=params)
                )(self.endpoint, **self.request_value)
            except Exception as error:
                self._unsuccessful_response_handler(error, body)
                continue
            finally:
                self._finally_response_handler()
            if response.status_code != HTTPStatus.OK:
                self._negative_response_status_handler(response, body)
                continue
            self._successful_response_handler()
            return response.json()
        return False

    def _create_headers(self, body=None) -> None:
        """
        Method that create headers for request.
        """
        self.headers = {'Content-Type': self.content_type}
        if self.fake_useragent and self.user_agent_spoiled:
            user_agent = random.choice(
                self.custom_user_agent
            ) or self.user_agent.__getattr__(self.user_agent_browser)
            self.headers['User-Agent'] = user_agent
        if body is not None and self.count_try <= 0:
            self.headers['Content-Length'] = str(len(json.dumps(body)))
        self.connection.session.headers.update(self.headers)

    def _successful_response_handler(self) -> None:
        """
        Logs a message when a response is successfully handled.
        """
        message = (f'Successful response with class: '
                   f'{self.__class__.__name__}')
        self.logger.info(message)

    def _unsuccessful_response_handler(self, error: Exception,
                                       body: dict | None) -> None:
        """
        Logs an error message when a response cannot be handled.
        """
        message = (f'{error} with response, class: '
                   f'{self.__class__.__name__}, count try: {self.count_try}')
        self.logger.error(message)
        self.__renew_connection(body)

    def _negative_response_status_handler(self, response: requests.Response,
                                          body: dict | None) -> None:
        """
        Logs an error message when the response status code is not OK.
        """
        message = (f'{response.status_code} status code with response, class: '
                   f'{self.__class__.__name__}, count try: {self.count_try}')
        self.logger.error(message)
        self.__renew_connection(body)

    def _finally_response_handler(self) -> None:
        """
        Records the time spent connecting to API.
        """
        connections_duration = (
            datetime.now(timezone.utc) - self.connection_start_time
        ).seconds
        self.connections_duration += round(connections_duration, 2)
        time.sleep(self.waiting_time)

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


class BaseCryptoParser(BaseParser, ABC):
    """
    This abstract class is a subclass of BaseParser. It extends the class
    initialization required for all crypto-parsers.

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
            ALL_FIATS, CRYPTO_EXCHANGES_CONFIG, TRADE_TYPES)
        self.crypto_exchanges_configs = CRYPTO_EXCHANGES_CONFIG.get(
            self.crypto_exchange_name)
        self.assets = self.crypto_exchanges_configs.get('assets')
        self.all_fiats = set(ALL_FIATS)
        self.crypto_exchange = CryptoExchanges.objects.get(
            name=self.crypto_exchange_name
        )
        self.trade_types = TRADE_TYPES


class BankParser(BaseParser, ABC):
    """
    This class is a subclass of BaseParser and ABC. It parses bank exchange
    rates data from API, calculates the buy and sell data or the price data,
    and updates the database.

    Attributes:
        model: The Django model representing the bank exchange rates.
        model_update: The Django model representing the updates of the bank
            exchange rates.
        updated_fields (list): A list of strings representing the
            fields to update in the model.
        request_method (str): The type of the request method.
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
    request_method: str = 'get'
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

    def _generate_unique_params(self) -> List[Dict[str]]:
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

    def _calculates_buy_and_sell_data(self, params: Dict[str]
                                      ) -> tuple[dict, dict] | None:
        """
        Calculates the buy and sell data for a given set of
        parameters. It gets the API response using the _send_request
        method, extracts the buy and sell data using the
        _extract_buy_and_sell_from_json method, and returns a tuple of
        dictionaries containing the calculated buy and sell data.
        """
        response_json = self._send_request(params=params)
        if response_json is False:
            return None
        buy_and_sell = self._extract_buy_and_sell_from_json(response_json)
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

    def _calculates_price_data(self, params: Dict[str]
                               ) -> list[dict[str, Any]] | None:
        """
        Calculates the price data for a given set of parameters.
        It gets the API response using the _send_request method, extracts
        the price data using the _extract_price_from_json method, and returns a
        list of dictionaries containing the calculated price data.
        """
        response_json = self._send_request(params=params)
        if response_json is False:
            return None
        price = self._extract_price_from_json(response_json)
        price_data = {
            'from_fiat': params[self.name_from],
            'to_fiat': params[self.name_to],
            'price': price
        }
        return [price_data]

    def _calculates_all_values_data(self) -> List[dict[str, Any]] | None:
        """
        Calculates all values data. It gets the API response using the
        _send_request method, extracts all values data using the
        _extract_all_values_from_json method, and returns a list of
        dictionaries containing the calculated data, or None if no data is
        available.
        """
        response_json = self._send_request()
        if response_json is False:
            return None
        return self._extract_all_values_from_json(response_json)

    def _choice_buy_and_sell_or_price(
            self, params=None
    ) -> Union[tuple[dict, dict], list[dict], None]:
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


class BankInvestParser(BaseParser, ABC):
    """
    This class parses exchange rates data from Bank Invest website and stores
    it in the database. It inherits from `BaseParser` and `ABC`.

    Attributes:
        model: The Django model to use for creating or updating exchange rates
            data.
        model_update: The Django model to use for creating update objects.
        updated_fields (list): The fields to update when updating exchange
            rates data.
        request_method (str): The type of the request method.
        currency_markets_name (str): The name of the currency market to use
            when creating or updating exchange rates data.
        link_ends (str): The string of link ends to use when constructing the
            URLs to make requests to the Bank Invest API.
    """
    model = BanksExchangeRates
    model_update = BanksExchangeRatesUpdates
    updated_fields: List[str] = ['price', 'update']
    request_method: str = 'get'
    currency_markets_name: str
    link_ends: str

    def __init__(self) -> None:
        super().__init__()
        self.currency_market = CurrencyMarkets.objects.get(
            name=self.currency_markets_name)
        self.new_update = self.model_update.objects.create(
            currency_market=self.currency_market
        )

    def _get_api_answer(self, link_end: str) -> dict | None:
        """
        Makes a GET request to the Bank Invest API and returns the response
        data as a dictionary.
        """
        self.endpoint = self.endpoint + link_end
        return self._send_request()

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


class P2PParser(BaseCryptoParser, ABC):
    """
    This class is a subclass of the BaseCryptoParser class and represents a
    parser for peer-to-peer exchanges rates. It has the following attributes.

    Attributes:
        model: A Django model representing the exchange rates to be parsed.
        model_update: A Django model representing the updates to be made to
            the exchange rates.
        updated_fields (list): A list of fields to be updated in the model
            when new exchange rates are fetched.
        request_method (str): The type of the request method.
        bank_name (str): Representing the name of the bank to be parsed.
        page (int): Representing the page number to be parsed.
        rows (int): Representing the number of rows to be parsed.
        payment_channel: A string representing the payment channel for which
            the exchange rates are to be fetched.
    """
    model = CryptoExchangesRates
    model_update = CryptoExchangesRatesUpdates
    updated_fields: List[str] = ['price', 'update']
    request_method: str = 'post'
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
        self.banks_configs = self.banks_config[self.bank_name]
        self.fiats = set(self.banks_configs['currencies'])
        self.if_no_objects = self.model.objects.filter(
            crypto_exchange=self.crypto_exchange,
            payment_channel=self.payment_channel
        ).count() == 0
        self.if_new_hour = datetime.now(
            timezone.utc
        ).time().minute < self.model_update.objects.last().updated.time(
        ).minute
        self.full_update = self.if_no_objects or self.if_new_hour

    @ abstractmethod
    def _check_supports_fiat(self, fiat: str) -> bool:
        """
        This method will check if a given bank supports a particular currency
        on a particular crypto exchange.
        """
        pass

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
        return self._send_request(body=body)

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
            if not self._check_supports_fiat(fiat):
                continue
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


class CryptoExchangesParser(BaseCryptoParser, ABC):
    """
    A base parser class for extracting intra-exchange cryptocurrency rates data
    from different cryptocurrency exchanges.

    Attributes:
        model: A Django model representing the exchange rates to be parsed.
        model_update: A Django model representing the updates to be made to
            the exchange rates.
        updated_fields (list): A list of fields to be updated in the model
            when new exchange rates are fetched.
        request_method (str): The type of the request method.
        name_from (str): Representing the name of the params key.
        base_spot_fee (float): The exchange's base commission for buying and
            selling.
        zero_fees (dict): Dictionary of our assets pairs in which the
            commission is zero.
    """
    model = IntraCryptoExchangesRates
    model_update = IntraCryptoExchangesRatesUpdates
    updated_fields: List[str] = ['price', 'update']
    request_method: str = 'get'
    exceptions: tuple = tuple()
    name_from: str
    base_spot_fee: float
    zero_fees: Dict[str, Tuple[str]]

    def __init__(self) -> None:
        super().__init__()
        self.new_update = self.model_update.objects.create(
            crypto_exchange=self.crypto_exchange
        )
        self.crypto_fiats = self.crypto_exchanges_configs.get('crypto_fiats')

    def _create_params(self, assets_combinations: tuple
                       ) -> List[dict[str, str]]:
        """
        Method that creates parameters for the cryptocurrency exchange API
        endpoint.
        """
        return [
            dict([(self.name_from, ''.join([params[0], params[1]]))])
            for params in assets_combinations
            if ''.join([params[0], params[1]]) not in self.exceptions
        ]

    def _get_api_answer(
            self, params: dict[str, str]
    ) -> Union[tuple[Dict[str, Any], dict[str, str]], bool]:
        """
        Method that sends a request to the cryptocurrency exchange API
        endpoint and returns the response.
        """
        response = self._send_request(params=params)
        if not response:
            message = f'Unsuccessful response with params: {params}'
            self.logger.error(message)
            return False
        return response, params

    @staticmethod
    @abstractmethod
    def _extract_price_from_json(json_data: dict) -> float:
        """
        Abstract method that extracts the price data from the cryptocurrency
        exchange API response.
        """
        pass

    def _calculates_buy_and_sell_data(self, params: dict[str, str]
                                      ) -> tuple[dict, dict] | None:
        """
        Method that calculates the buy and sell data for each cryptocurrency
        asset pair.
        """
        answer = self._get_api_answer(params)
        if not answer:
            return None
        json_data, valid_params = answer
        price = self._extract_price_from_json(json_data)
        for from_asset in self.assets + self.crypto_fiats:
            if from_asset in valid_params['symbol'][0:4]:
                for to_asset in self.assets + self.crypto_fiats:
                    if to_asset in valid_params['symbol'][-4:]:
                        spot_fee = self._calculates_spot_fee(from_asset,
                                                             to_asset)
                        buy_data = {
                            'from_asset': from_asset,
                            'to_asset': to_asset,
                            'price': price - price / 100 * spot_fee,
                            'spot_fee': spot_fee
                        }
                        sell_data = {
                            'from_asset': to_asset,
                            'to_asset': from_asset,
                            'price': (
                                1.0 / price - (1.0 / price) / 100 * spot_fee
                            ),
                            'spot_fee': spot_fee
                        }
                        return buy_data, sell_data

    def _calculates_spot_fee(self, from_asset: str, to_asset: str
                             ) -> int | float:
        """
        This method calculates the commission for the exchange within the
        crypto exchange.
        """
        from_asset_fee_list = self.zero_fees.get(from_asset)
        if from_asset_fee_list is not None:
            if to_asset in from_asset_fee_list:
                return 0
        to_asset_fee_list = self.zero_fees.get(to_asset)
        if to_asset_fee_list is not None:
            if from_asset in to_asset_fee_list:
                return 0
        return self.base_spot_fee

    def _generate_unique_params(self) -> List[dict[str, str]]:
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


class ListsFiatCryptoParser(BaseCryptoParser, ABC):
    """
    This class is a subclass of BaseCryptoParser abstract class. Represents a
    parser for parsing exchange rates from a specific API. The exchange rates
    are related to the list of fiat and cryptocurrencies supported by a
    specific exchange.

    Attributes:
        model: A Django model representing the exchange rates to be parsed.
        model_update: A Django model representing the updates to be made to
            the exchange rates.
        updated_fields (list): A list of fields to be updated in the model
            when new exchange rates are fetched.
        request_method (str): The type of the request method.
        endpoint_sell (str): the API endpoint for fetching the sell rates.
        endpoint_buy (str): the API endpoint for fetching the buy rates.
    """
    model = ListsFiatCrypto
    model_update = ListsFiatCryptoUpdates
    updated_fields: List[str] = ['list_fiat_crypto', 'update']
    request_method: str = 'post'
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

    def _get_api_answer(self, asset=None, fiat=None) -> dict | None:
        """
        A method that makes a request to the API to fetch either the sell or
        buy rates, depending on the input parameters.
        """
        if asset:
            body = self._create_body_sell(asset)
            self.endpoint = self.endpoint_sell
        else:  # if fiat
            body = self._create_body_buy(fiat)
            self.endpoint = self.endpoint_buy
        return self._send_request(body=body)

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


class Card2CryptoExchangesParser(BaseCryptoParser, ABC):
    """
    This class is derived from BaseCryptoParser class and inherits all of its
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
            crypto_exchange=self.crypto_exchange,
            payment_channel=self.payment_channel
        ).count() == 0
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

    def _get_api_answer(self, asset: str, fiat: str, amount: int
                        ) -> dict | bool:
        """
        Returns the API response for a given asset, fiat and amount.
        """
        if self.trade_type == 'SELL':
            body = self._create_body_sell(fiat, asset, amount)
            self.endpoint = self.endpoint_sell
            return self._send_request(body=body)
        params = self._create_params_buy(fiat, asset)
        self.endpoint = self.endpoint_buy
        return self._send_request(params=params)

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
                if response is False:
                    continue
                values = self._extract_values_from_json(response, amount)
                if values is None:
                    continue
                price, pre_price, commission = values
                self._add_to_bulk_update_or_create(
                    asset, fiat, price, pre_price, commission
                )
