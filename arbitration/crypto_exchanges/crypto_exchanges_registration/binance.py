from __future__ import annotations

import os
from abc import ABC
from itertools import combinations
from typing import List, Tuple

from arbitration.settings import (API_BINANCE_CARD_2_CRYPTO_BUY,
                                  API_BINANCE_CARD_2_CRYPTO_SELL,
                                  API_BINANCE_CRYPTO,
                                  API_BINANCE_LIST_FIAT_BUY,
                                  API_BINANCE_LIST_FIAT_SELL, API_P2P_BINANCE,
                                  CONNECTION_TYPE_BINANCE_CARD_2_CRYPTO,
                                  CONNECTION_TYPE_BINANCE_CRYPTO,
                                  CONNECTION_TYPE_BINANCE_LIST_FIAT,
                                  CONNECTION_TYPE_P2P_BINANCE)
from parsers.calculations import Card2Wallet2CryptoExchangesCalculating
from parsers.parsers import (Card2CryptoExchangesParser, CryptoExchangesParser,
                             ListsFiatCryptoParser, P2PParser)

CRYPTO_EXCHANGES_NAME = os.path.basename(__file__).split('.')[0].capitalize()

BINANCE_ASSETS = ('ADA', 'BNB', 'ETH', 'BTC', 'SHIB', 'BUSD', 'USDT')  # 'DAI',
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
BINANCE_INVALID_PARAMS_LIST = (
    ('DAI', 'AUD'), ('DAI', 'BRL'), ('DAI', 'EUR'), ('DAI', 'GBP'),
    ('DAI', 'RUB'), ('DAI', 'TRY'), ('DAI', 'UAH'), ('BNB', 'SHIB'),
    ('ETH', 'SHIB'), ('BTC', 'SHIB'), ('DAI', 'SHIB'), ('ADA', 'DAI'),
    ('ADA', 'SHIB'), ('ADA', 'UAH')
)
BINANCE_CRYPTO_FIATS = ('AUD', 'BRL', 'EUR', 'GBP', 'RUB', 'TRY', 'UAH')
BINANCE_DEPOSIT_FIATS = {
    'RUB': (('Bank Card (Visa/MS/МИР)', 1.2),),
    'UAH': (('SettlePay (Visa/MC)', 1.5),),
    'EUR': (('Bank Card (Visa/MC)', 1.8),),
    'GBP': (('Bank Card (Visa/MC)', 1.8),),
    'TRY': (('Turkish Bank Transfer', 0),),
}
BINANCE_WITHDRAW_FIATS = {
    'RUB': (('Bank Card (Visa/MS/МИР)', 0),),
    'UAH': (('SettlePay (Visa/MC)', 1),),
    'EUR': (('Bank Card (Visa)', 1.8),),
    'GBP': (('Bank Card (Visa)', 1.8),),
    'TRY': (('Turkish Bank Transfer', 0),),
}
BINANCE_SPOT_ZERO_FEES = {
    'BTC': [
        'AUD', 'BIDR', 'BRL', 'BUSD', 'EUR', 'GBP', 'RUB', 'TRY', 'TUSD',
        'UAH', 'USDC', 'USDP', 'USDT'
    ]
}


class BinanceP2PParser(P2PParser, ABC):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    endpoint: str = API_P2P_BINANCE
    connection_type: str = CONNECTION_TYPE_P2P_BINANCE
    need_cookies: bool = False
    page: int = 1
    rows: int = 1
    # custom_settings
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
    connection_type: str = CONNECTION_TYPE_BINANCE_CRYPTO
    need_cookies: bool = False
    fake_useragent: bool = False
    exceptions: tuple = ('SHIBRUB', 'RUBSHIB', 'SHIBGBP', 'GBPSHIB')
    name_from: str = 'symbol'
    base_spot_fee: float = 0.1
    zero_fees: dict = BINANCE_SPOT_ZERO_FEES
    # custom_settings
    stablecoins: Tuple[str] = ('USDT', 'BUSD')

    @staticmethod
    def _extract_price_from_json(json_data: dict) -> float:
        return float(json_data['price'])

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
                if asset in self.stablecoins and crypto_fiat in (
                        'EUR', 'GBP', 'AUD'):
                    currencies_combinations.append((crypto_fiat, asset))
                else:
                    currencies_combinations.append((asset, crypto_fiat))
        currencies_combinations = tuple(
            currencies_combination for currencies_combination
            in currencies_combinations
            if currencies_combination not in invalid_params_list
        )
        return self._create_params(currencies_combinations)


class BinanceCard2CryptoExchangesParser(Card2CryptoExchangesParser):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    endpoint_sell: str = API_BINANCE_CARD_2_CRYPTO_SELL
    endpoint_buy: str = API_BINANCE_CARD_2_CRYPTO_BUY
    connection_type: str = CONNECTION_TYPE_BINANCE_CARD_2_CRYPTO
    need_cookies: bool = False

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
    connection_type: str = CONNECTION_TYPE_BINANCE_LIST_FIAT
    need_cookies: bool = False

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
