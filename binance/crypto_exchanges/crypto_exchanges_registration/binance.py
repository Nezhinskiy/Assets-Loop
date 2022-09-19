from __future__ import annotations

import os
from http import HTTPStatus
from sys import getsizeof

import requests

from banks.banks_config import BANKS_CONFIG
from core.intra_exchanges import BestCryptoExchanges
from core.parsers import (Card2CryptoExchangesParser,
                          Card2Wallet2CryptoExchangesParser,
                          CryptoExchangesParser, ListsFiatCryptoParser,
                          P2PParser)

CRYPTO_EXCHANGES_NAME = os.path.basename(__file__).split('.')[0].capitalize()

BINANCE_ASSETS = ('ETH', 'BTC', 'BUSD', 'USDT')
BINANCE_TRADE_TYPES = ('BUY', 'SELL')
BINANCE_FIATS = ('RUB', 'USD', 'EUR')
BINANCE_CRYPTO_FIATS = ('AUD', 'BRL', 'EUR', 'GBP', 'RUB', 'TRY', 'UAH')
BINANCE_PAY_TYPES = (pay_type for pay_type in BANKS_CONFIG.keys())
DEPOSIT_FIATS = {
    'UAH': (('SettlePay (Visa/MC)', 1.5),),
    'EUR': (('Bank Card (Visa/MC)', 1.8),),
    'GBP': (('Bank Card (Visa/MC)', 1.8),),
    'TRY': (('Turkish Bank Transfer', 0),),
}
WITHDRAW_FIATS = {
    'UAH': (('SettlePay (Visa/MC)', 1),),
    'EUR': (('Bank Card (Visa)', 1.8),),
    'GBP': (('Bank Card (Visa)', 1.8),),
    'TRY': (('Turkish Bank Transfer', 0),),
}

ASSETS = (
    ('ETH', 'ETH'),
    ('BTC', 'BTC'),
    ('BUSD', 'BUSD'),
    ('USDT', 'USDT'),
)

TRADE_TYPES = (
    ('BUY', 'buy'),
    ('SELL', 'sell')
)
FIATS = (
    ('RUB', 'rub'),
    # ('USD', 'usd'),
    # ('EUR', 'eur'),
    # ('GBP', 'gbp'),
)
CRYPTO_FIATS = (
    'AUD', 'BRL', 'EUR', 'GBP', 'RUB', 'TRY', 'UAH'
)
PAY_TYPES = (
    ('Tinkoff', 'Tinkoff'),
    ('Wise', 'Wise'),
    # 'TBCbank',
    # 'BankofGeorgia',
    ('RosBank', 'RosBank'),
    ('RUBfiatbalance', 'RUBfiatbalance')
)


class BinanceP2PParser(P2PParser):
    crypto_exchange_name = CRYPTO_EXCHANGES_NAME
    assets = ASSETS
    fiats = FIATS
    trade_types = TRADE_TYPES
    endpoint = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
    page = 1
    rows = 1

    def create_body(self, asset, bank, fiat, pay_types):
        return {
            "page": self.page,
            "rows": self.rows,
            "publisherType": None,
            "asset": asset,
            "tradeType": bank,
            "fiat": fiat,
            "payTypes": [pay_types]
        }

    def create_headers(self, body):
        return {
            "Content-Type": "application/json",
            "Content-Length": str(getsizeof(body)),
        }

    def extract_price_from_json(self, json_data: dict) -> [int | None]:
        data = json_data.get('data')
        if len(data) == 0:
            price = None
            return price
        internal_data = data[0]
        adv = internal_data.get('adv')
        price = adv.get('price')
        return price


class BinanceCryptoParser(CryptoExchangesParser):
    crypto_exchange_name = CRYPTO_EXCHANGES_NAME
    fiats = ASSETS
    endpoint = 'https://api.binance.com/api/v3/ticker/price?'
    name_from = 'symbol'

    def get_api_answer(self, params):
        """Делает запрос к эндпоинту API Tinfoff."""
        try:
            response = requests.get(self.endpoint, params)
        except Exception as error:
            message = f'Ошибка при запросе к основному API: {error}'
            raise Exception(message)
        if response.status_code != HTTPStatus.OK:
            params = {
                self.name_from:
                    params[self.name_from][4:] + params[self.name_from][:4]
            }
            response = requests.get(self.endpoint, params)
        return response.json()

    def converts_choices_to_set(self, choices: tuple[tuple[str, str]]
                                ) -> list[str]:
        """repackaging choices into a set."""
        return [choice[0] for choice in choices]

    def extract_price_from_json(self, json_data) -> float:
        price: float = float(json_data['price'])
        return price

    def create_params(self, fiats_combinations):
        params = [
            dict([(self.name_from, ''.join([params[0], params[1]]))])
            for params in fiats_combinations
        ]
        return params

    def calculates_buy_and_sell_data(self, params) -> tuple[dict, dict]:
        price = self.extract_price_from_json(self.get_api_answer(params))
        for from_fiat in BINANCE_ASSETS + BINANCE_CRYPTO_FIATS:
            if from_fiat in params['symbol'][0:4]:
                for to_fiat in BINANCE_ASSETS + BINANCE_CRYPTO_FIATS:
                    if to_fiat in params['symbol'][-4:]:
                        buy_data = {
                            'from_asset': from_fiat,
                            'to_asset': to_fiat,
                            'price': round(price, self.ROUND_TO)
                        }
                        sell_data = {
                            'from_asset': to_fiat,
                            'to_asset': from_fiat,
                            'price': round(1.0 / price, self.ROUND_TO)
                        }
                        return buy_data, sell_data


class BinanceCard2CryptoExchangesParser(Card2CryptoExchangesParser):
    crypto_exchange_name = CRYPTO_EXCHANGES_NAME
    endpoint_sell = 'https://www.binance.com/bapi/fiat/v1/public/ocbs/get-quote'
    endpoint_buy = 'https://www.binance.com/bapi/fiat/v2/public/ocbs/fiat-channel-gateway/get-quotation?'


class BinanceListsFiatCryptoParser(ListsFiatCryptoParser):
    crypto_exchange_name = CRYPTO_EXCHANGES_NAME
    endpoint_sell = 'https://www.binance.com/bapi/fiat/v2/friendly/ocbs/sell/list-fiat'
    endpoint_buy = 'https://www.binance.com/bapi/fiat/v2/friendly/ocbs/buy/list-crypto'


def get_binance_card_2_crypto_exchanges():
    binance_card_2_crypto_exchanges_parser = BinanceCard2CryptoExchangesParser()
    message = binance_card_2_crypto_exchanges_parser.main()
    return message


def get_binance_fiat_crypto_list():
    binance_fiat_crypto_list_parser = BinanceListsFiatCryptoParser()
    message = binance_fiat_crypto_list_parser.main()
    return message


def get_all_binance_crypto_exchanges():
    binance_crypto_parser = BinanceCryptoParser()
    message = binance_crypto_parser.main()
    return message


def get_all_p2p_binance_exchanges():
    binance_parser = BinanceP2PParser()
    message = binance_parser.main()
    return message


def get_all_card_2_wallet_2_crypto_exchanges():
    card_2_wallet_2_crypto_exchanges_parser = Card2Wallet2CryptoExchangesParser(
        CRYPTO_EXCHANGES_NAME)
    message = card_2_wallet_2_crypto_exchanges_parser.main()
    return message


def get_best_crypto_exchanges():
    best_intra_crypto_exchanges = BestCryptoExchanges(CRYPTO_EXCHANGES_NAME)
    message = best_intra_crypto_exchanges.main()
    return message
