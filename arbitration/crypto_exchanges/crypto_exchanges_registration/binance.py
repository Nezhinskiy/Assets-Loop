from __future__ import annotations

import os
from abc import ABC
from http import HTTPStatus
from sys import getsizeof
from time import sleep
from typing import List, Dict

import requests

from banks.banks_config import BANKS_CONFIG
from core.calculations import InterExchangesCalculating, Card2Wallet2CryptoExchangesCalculating
from core.parsers import (Card2CryptoExchangesParser,
                          CryptoExchangesParser, ListsFiatCryptoParser,
                          P2PParser)

CRYPTO_EXCHANGES_NAME = os.path.basename(__file__).split('.')[0].capitalize()

BINANCE_ASSETS = ('ADA', 'BNB', 'ETH', 'BTC', 'BUSD', 'USDT', 'SHIB')  # 'DAI',
BINANCE_ASSETS_FOR_FIAT = {
    'all': ('USDT', 'BTC', 'BUSD', 'ETH'),
    'RUB': ('USDT', 'BTC', 'BUSD', 'BNB', 'ETH', 'SHIB', 'RUB'),
    'USD': ('USDT', 'BTC', 'BUSD', 'BNB', 'ETH',),# 'DAI'),
    'EUR': ('USDT', 'BTC', 'BUSD', 'BNB', 'ETH',),# 'DAI', 'SHIB'),
    'GBP': ('USDT', 'BTC', 'BUSD', 'BNB', 'ETH',),# 'DAI'),
    'CHF': ('USDT', 'BTC', 'BUSD', 'BNB', 'ETH',),# 'DAI'),
    'CAD': ('USDT', 'BTC', 'BUSD', 'BNB', 'ETH',),# 'DAI'),
    'AUD': ('USDT', 'BTC', 'BUSD', 'BNB', 'ETH', 'SHIB', 'ADA'),
    'GEL': ('USDT', 'BTC', 'BUSD', 'BNB', 'ETH')
}
INVALID_PARAMS_LIST = (
    ('DAI', 'AUD'), ('DAI', 'BRL'), ('DAI', 'EUR'), ('DAI', 'GBP'),
    ('DAI', 'RUB'), ('DAI', 'TRY'), ('DAI', 'UAH'), ('BNB', 'SHIB'),
    ('ETH', 'SHIB'), ('BTC', 'SHIB'), ('DAI', 'SHIB'), ('ADA', 'DAI'),
    ('ADA', 'SHIB'), ('ADA', 'UAH')
)
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
CRYPTO_FIATS = (
    'AUD', 'BRL', 'EUR', 'GBP', 'RUB', 'TRY', 'UAH'
)
SPOT_ZERO_FEES = {
    'BTC': [
        'AUD', 'BIDR', 'BRL', 'BUSD', 'EUR', 'GBP', 'RUB', 'TRY', 'TUSD',
        'UAH', 'USDC', 'USDP', 'USDT'
    ]
}


class BinanceP2PParser(P2PParser, ABC):
    crypto_exchange_name = CRYPTO_EXCHANGES_NAME
    endpoint = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
    page = 1
    rows = 1

    def create_body(self, asset: str, fiat: str, trade_type: str) -> dict:
        return {
            "page": self.page,
            "rows": self.rows,
            "publisherType": "merchant",
            "asset": asset,
            "tradeType": trade_type,
            "fiat": fiat,
            "payTypes": [self.bank.binance_name]
        }

    @staticmethod
    def extract_price_from_json(json_data: dict) -> float | None:
        data = json_data.get('data')
        if len(data) == 0:
            return
        internal_data = data[0]
        adv = internal_data.get('adv')
        return float(adv.get('price'))


class TinkoffBinanceP2PParser(BinanceP2PParser):
    bank_name = 'Tinkoff'


class WiseBinanceP2PParser(BinanceP2PParser):
    bank_name = 'Wise'


class BinanceCryptoParser(CryptoExchangesParser):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    fiats: tuple = ASSETS
    endpoint: str = 'https://api.binance.com/api/v3/ticker/price?'
    exceptions: tuple = ('SHIBRUB',)
    name_from: int = 'symbol'

    def get_api_answer(self, params):
        """Делает запрос к эндпоинту API Tinfoff."""
        try:
            try:
                with requests.session() as session:
                    response = session.get(self.endpoint, params=params)
            except Exception as error:
                message = f'Ошибка при запросе к основному API: {error}'
                print(message)
                # raise Exception(message)
            if response.status_code != HTTPStatus.OK:
                params = {
                    self.name_from:
                        params[self.name_from][4:] + params[self.name_from][:4]
                }
                sleep(1)
                with requests.session() as session:
                    response = session.get(self.endpoint, params=params)
            return response.json(), params
        except Exception as error:
            message = f'Ошибка при запросе к основному API: {error}'
            print(message)
            # raise Exception(message)
            return False

    @staticmethod
    def extract_price_from_json(json_data: dict) -> float:
        return float(json_data['price'])

    def create_params(self,
                      assets_combinations: tuple) -> list[dict[int, str]]:
        return [
            dict([(self.name_from, ''.join([params[0], params[1]]))])
            for params in assets_combinations if params not in self.exceptions
        ]

    def calculates_buy_and_sell_data(self, params) -> tuple[dict, dict] | None:
        answer = self.get_api_answer(params)
        if not answer:
            return
        json_data, valid_params = answer
        price = self.extract_price_from_json(json_data)
        for from_fiat in BINANCE_ASSETS + BINANCE_CRYPTO_FIATS:
            if from_fiat in valid_params['symbol'][0:4]:
                for to_fiat in BINANCE_ASSETS + BINANCE_CRYPTO_FIATS:
                    if to_fiat in valid_params['symbol'][-4:]:
                        if (
                                to_fiat in SPOT_ZERO_FEES.keys()
                                and from_fiat in SPOT_ZERO_FEES.get(to_fiat)
                                or from_fiat in SPOT_ZERO_FEES.keys()
                                and to_fiat in SPOT_ZERO_FEES.get(from_fiat)
                        ):
                            spot_fee = 0
                        else:
                            spot_fee = 0.1
                        buy_data = {
                            'from_asset': from_fiat,
                            'to_asset': to_fiat,
                            'price': price - price / 100 * spot_fee,
                            'spot_fee': spot_fee
                        }
                        sell_data = {
                            'from_asset': to_fiat,
                            'to_asset': from_fiat,
                            'price': (1.0 / price -
                                      (1.0 / price) / 100 * spot_fee),
                            'spot_fee': spot_fee
                        }
                        return buy_data, sell_data


class BinanceCard2CryptoExchangesParser(Card2CryptoExchangesParser):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    endpoint_sell: str = 'https://www.binance.com/bapi/fiat/v1/public/ocbs/get-quote'
    endpoint_buy: str = 'https://www.binance.com/bapi/fiat/v2/public/ocbs/fiat-channel-gateway/get-quotation?'


class BinanceListsFiatCryptoParser(ListsFiatCryptoParser):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    endpoint_sell: str = 'https://www.binance.com/bapi/fiat/v2/friendly/ocbs/sell/list-fiat'
    endpoint_buy: str = 'https://www.binance.com/bapi/fiat/v2/friendly/ocbs/buy/list-crypto'


class BinanceCard2Wallet2CryptoExchangesCalculating(Card2Wallet2CryptoExchangesCalculating):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME


class SimplBinanceTinkoffInterExchangesCalculating(InterExchangesCalculating):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    bank_name: str = 'Tinkoff'
    simpl: bool = True


class SimplBinanceWiseInterExchangesCalculating(InterExchangesCalculating):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    bank_name: str = 'Wise'
    simpl: bool = True


class ComplexBinanceTinkoffInterExchangesCalculating(
    InterExchangesCalculating
):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    bank_name: str = 'Tinkoff'
    simpl: bool = False


class ComplexBinanceWiseInterExchangesCalculating(
    InterExchangesCalculating
):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    bank_name: str = 'Wise'
    simpl: bool = False
