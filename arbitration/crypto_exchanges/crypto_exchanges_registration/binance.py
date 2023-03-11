from __future__ import annotations

import os
from abc import ABC
from http import HTTPStatus
from time import sleep
from typing import List, Tuple

import requests

from arbitration.settings import (API_BINANCE_CARD_2_CRYPTO_BUY,
                                  API_BINANCE_CARD_2_CRYPTO_SELL,
                                  API_BINANCE_CRYPTO,
                                  API_BINANCE_LIST_FIAT_BUY,
                                  API_BINANCE_LIST_FIAT_SELL, API_P2P_BINANCE)
from core.calculations import (Card2Wallet2CryptoExchangesCalculating,
                               InterExchangesCalculating)
from core.parsers import (Card2CryptoExchangesParser, CryptoExchangesParser,
                          ListsFiatCryptoParser, P2PParser)

CRYPTO_EXCHANGES_NAME = os.path.basename(__file__).split('.')[0].capitalize()

BINANCE_ASSETS = ('ADA', 'BNB', 'ETH', 'BTC', 'BUSD', 'USDT', 'SHIB')  # 'DAI',
BINANCE_ASSETS_FOR_FIAT = {
    'all': ('USDT', 'BTC', 'BUSD', 'ETH'),
    'RUB': ('USDT', 'BTC', 'BUSD', 'BNB', 'ETH', 'SHIB', 'RUB'),
    'USD': ('USDT', 'BTC', 'BUSD', 'BNB', 'ETH',),  # 'DAI'),
    'EUR': ('USDT', 'BTC', 'BUSD', 'BNB', 'ETH',),  # 'DAI', 'SHIB'),
    'GBP': ('USDT', 'BTC', 'BUSD', 'BNB', 'ETH',),  # 'DAI'),
    'CHF': ('USDT', 'BTC', 'BUSD', 'BNB', 'ETH',),  # 'DAI'),
    'CAD': ('USDT', 'BTC', 'BUSD', 'BNB', 'ETH',),  # 'DAI'),
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
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    endpoint: str = API_P2P_BINANCE
    page: int = 1
    rows: int = 1
    exception_fiats: Tuple[str] = ('USD', 'EUR')

    def _check_supports_fiat(self, fiat: str) -> bool:
        from banks.banks_config import RUS_BANKS
        if self.bank_name in RUS_BANKS and fiat in self.exception_fiats:
            return False
        return True

    def _create_body(self, asset: str, fiat: str, trade_type: str) -> dict:
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
    def _extract_price_from_json(json_data: dict) -> float | None:
        data = json_data.get('data')
        if len(data) == 0:
            return None
        internal_data = data[0]
        adv = internal_data.get('adv')
        return float(adv.get('price'))


class BinanceCryptoParser(CryptoExchangesParser):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    endpoint: str = API_BINANCE_CRYPTO
    exceptions: tuple = ('SHIBRUB', 'RUBSHIB', 'SHIBGBP', 'GBPSHIB')
    name_from: int = 'symbol'
    zero_fees = SPOT_ZERO_FEES

    def _get_api_answer(self, params):
        """Делает запрос к эндпоинту API Tinfoff."""
        try:
            try:
                with requests.session() as session:
                    response = session.get(self.endpoint, params=params)
            except Exception as error:
                self._unsuccessful_response_handler(error)
            if response.status_code != HTTPStatus.OK:
                params = {
                    self.name_from:
                        params[self.name_from][4:] + params[self.name_from][:4]
                }
                sleep(1)
                with requests.session() as session:
                    response = session.get(self.endpoint, params=params)
            self._successful_response_handler()
            return response.json(), params
        except Exception as error:
            self._unsuccessful_response_handler(error)
            return False

    @staticmethod
    def _extract_price_from_json(json_data: dict) -> float:
        return float(json_data['price'])

    def _create_params(self, assets_combinations: tuple
                       ) -> list[dict[int, str]]:
        return [
            dict([(self.name_from, ''.join([params[0], params[1]]))])
            for params in assets_combinations
            if ''.join([params[0], params[1]]) not in self.exceptions
        ]

    def _calculates_spot_fee(self, from_asset, to_asset) -> int | float:
        from_asset_fee_list = self.zero_fees.get(from_asset)
        if from_asset_fee_list is not None:
            if to_asset in from_asset_fee_list:
                return 0
        to_asset_fee_list = self.zero_fees.get(to_asset)
        if to_asset_fee_list is not None:
            if from_asset in to_asset_fee_list:
                return 0
        return 0.1

    def _calculates_buy_and_sell_data(self, params
                                      ) -> tuple[dict, dict] | None:
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


class BinanceCard2CryptoExchangesParser(Card2CryptoExchangesParser):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    endpoint_sell: str = API_BINANCE_CARD_2_CRYPTO_SELL
    endpoint_buy: str = API_BINANCE_CARD_2_CRYPTO_BUY

    @staticmethod
    def _create_body_sell(fiat: str, asset: str, amount: int) -> dict:
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
    def _create_body_buy(fiat: str, asset: str, amount: int) -> dict:
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
    def _create_params_buy(fiat: str, asset: str) -> dict:
        return {
            'channelCode': 'card',
            'fiatCode': fiat,
            'cryptoAsset': asset
        }

    def _extract_values_from_json(self, json_data: dict, amount: int
                                  ) -> tuple | None:
        if self.trade_type == 'SELL':
            data = json_data['data'].get('rows')
            pre_price = data.get('quotePrice')
            if not pre_price:
                return None
            commission = data.get('totalFee') / amount
            price = pre_price / (1 + commission)
            commission *= 100
        else:  # BUY
            data = json_data['data']
            pre_price = data['price']
            if not pre_price:
                return None
            pre_price = float(pre_price)
            commission = 0.02
            price = 1 / (pre_price * (1 + commission))
            commission *= 100
        return price, pre_price, commission


class BinanceListsFiatCryptoParser(ListsFiatCryptoParser):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    endpoint_sell: str = API_BINANCE_LIST_FIAT_SELL
    endpoint_buy: str = API_BINANCE_LIST_FIAT_BUY

    @staticmethod
    def _create_body_sell(asset: str) -> dict:
        return {
            "channels": ["card"],
            "crypto": asset,
            "transactionType": "SELL"
        }

    @staticmethod
    def _create_body_buy(fiat: str) -> dict:
        return {
            "channels": ["card"],
            "fiat": fiat,
            "transactionType": "BUY"
        }

    def _extract_buy_or_sell_list_from_json(self, json_data: dict,
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


class BinanceCard2Wallet2CryptoExchangesCalculating(
    Card2Wallet2CryptoExchangesCalculating
):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME


class SimplBinanceInterExchangesCalculating(InterExchangesCalculating):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    simpl: bool = True
    international: bool = False


class SimplBinanceInternationalInterExchangesCalculating(
    InterExchangesCalculating
):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    simpl: bool = True
    international: bool = True


class ComplexBinanceInterExchangesCalculating(InterExchangesCalculating):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    simpl: bool = False
    international: bool = False


class ComplexBinanceInternationalInterExchangesCalculating(
    InterExchangesCalculating
):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    simpl: bool = False
    international: bool = True
