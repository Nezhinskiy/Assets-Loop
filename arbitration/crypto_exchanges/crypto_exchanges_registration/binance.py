from __future__ import annotations

import os
from http import HTTPStatus
from sys import getsizeof
from time import sleep

import requests

from banks.banks_config import BANKS_CONFIG
from core.intra_exchanges import InterSimplExchangesCalculate
from core.parsers import (Card2CryptoExchangesParser,
                          Card2Wallet2CryptoExchangesParser,
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
SPOT_ZERO_FEES = {
    'BTC': [
        'AUD', 'BIDR', 'BRL', 'BUSD', 'EUR', 'GBP', 'RUB', 'TRY', 'TUSD',
        'UAH', 'USDC', 'USDP', 'USDT'
    ]
}


class BinanceP2PParser(P2PParser):
    crypto_exchange_name = CRYPTO_EXCHANGES_NAME
    assets = ASSETS
    fiats = FIATS
    trade_types = TRADE_TYPES
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
    crypto_exchange_name = CRYPTO_EXCHANGES_NAME
    fiats = ASSETS
    endpoint = 'https://api.binance.com/api/v3/ticker/price?'
    name_from = 'symbol'

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
        price: float = float(json_data['price'])
        return price

    def create_params(self, fiats_combinations):
        params = [
            dict([(self.name_from, ''.join([params[0], params[1]]))])
            for params in fiats_combinations
        ]
        return params

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

    def get_all_api_answers(self):
        for params in self.generate_unique_params():
            values = self.calculates_buy_and_sell_data(params)
            if not values:
                continue
            for value_dict in values:
                price = value_dict.pop('price')
                self.add_to_bulk_update_or_create(value_dict, price)


class BinanceCard2CryptoExchangesParser(Card2CryptoExchangesParser):
    crypto_exchange_name = CRYPTO_EXCHANGES_NAME
    endpoint_sell = 'https://www.binance.com/bapi/fiat/v1/public/ocbs/get-quote'
    endpoint_buy = 'https://www.binance.com/bapi/fiat/v2/public/ocbs/fiat-channel-gateway/get-quotation?'


class BinanceListsFiatCryptoParser(ListsFiatCryptoParser):
    crypto_exchange_name = CRYPTO_EXCHANGES_NAME
    endpoint_sell = 'https://www.binance.com/bapi/fiat/v2/friendly/ocbs/sell/list-fiat'
    endpoint_buy = 'https://www.binance.com/bapi/fiat/v2/friendly/ocbs/buy/list-crypto'


class BinanceCard2Wallet2CryptoExchangesParser(Card2Wallet2CryptoExchangesParser):
    crypto_exchange_name = CRYPTO_EXCHANGES_NAME


class SimplBinanceTinkoffInterExchangesCalculate(InterSimplExchangesCalculate):
    crypto_exchange_name = CRYPTO_EXCHANGES_NAME
    bank_name = 'Tinkoff'
    simpl = True


class SimplBinanceWiseInterExchangesCalculate(InterSimplExchangesCalculate):
    crypto_exchange_name = CRYPTO_EXCHANGES_NAME
    bank_name = 'Wise'
    simpl = True


class ComplexBinanceTinkoffInterExchangesCalculate(
    InterSimplExchangesCalculate
):
    crypto_exchange_name = CRYPTO_EXCHANGES_NAME
    bank_name = 'Tinkoff'
    simpl = False


class ComplexBinanceWiseInterExchangesCalculate(
    InterSimplExchangesCalculate
):
    crypto_exchange_name = CRYPTO_EXCHANGES_NAME
    bank_name = 'Wise'
    simpl = False


def get_simpl_binance_tinkoff_inter_exchanges_calculate():
    simpl_binance_tinkoff_inter_exchanges_calculate = (
        SimplBinanceTinkoffInterExchangesCalculate()
    )
    simpl_binance_tinkoff_inter_exchanges_calculate.main()


def get_simpl_binance_wise_inter_exchanges_calculate():
    simpl_binance_wise_inter_exchanges_calculate = (
        SimplBinanceWiseInterExchangesCalculate()
    )
    simpl_binance_wise_inter_exchanges_calculate.main()


def get_complex_binance_tinkoff_inter_exchanges_calculate():
    complex_binance_tinkoff_inter_exchanges_calculate = (
        ComplexBinanceTinkoffInterExchangesCalculate()
    )
    complex_binance_tinkoff_inter_exchanges_calculate.main()


def get_complex_binance_wise_inter_exchanges_calculate():
    complex_binance_wise_inter_exchanges_calculate = (
        ComplexBinanceWiseInterExchangesCalculate()
    )
    complex_binance_wise_inter_exchanges_calculate.main()


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
    binance_crypto_parser.main()


def get_all_p2p_binance_exchanges():
    binance_parser = BinanceP2PParser()
    message = binance_parser.main()
    return message


def get_all_card_2_wallet_2_crypto_exchanges():
    card_2_wallet_2_crypto_exchanges_parser = BinanceCard2Wallet2CryptoExchangesParser()
    message = card_2_wallet_2_crypto_exchanges_parser.main()
    return message
