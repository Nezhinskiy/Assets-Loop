import os
from abc import ABC
from typing import Tuple

from arbitration.settings import (API_BYBIT_CRYPTO, API_P2P_BYBIT,
                                  CONNECTION_TYPE_BYBIT_CRYPTO,
                                  CONNECTION_TYPE_P2P_BYBIT)
from banks.models import BanksExchangeRates
from parsers.parsers import CryptoExchangesParser, P2PParser

CRYPTO_EXCHANGES_NAME = os.path.basename(__file__).split('.')[0].capitalize()

BYBIT_ASSETS = ('ETH', 'BTC', 'USDC', 'USDT')
BYBIT_CRYPTO_FIATS = ('EUR',)
BYBIT_ASSETS_FOR_FIAT = {'all': ('BTC', 'ETH', 'USDC', 'USDT')}
BYBIT_SPOT_ZERO_FEES = {
    'USDC': [
        'ADA', 'APE', 'APEX', 'BTC', 'DOGE', 'CHZ', 'DOT', 'EOS', 'ETH', 'BIT',
        'HFT', 'LDO', 'LTC', 'LUNC', 'SHIB', 'SLG', 'SOL', 'TRX', 'XRP'
    ],
    'USDT': [
        'BUSD', 'DAI', 'USDC'
    ],
    'BTC': [
        'WBTC'
    ]
}
BYBIT_INVALID_PARAMS_LIST = (('BTC', 'EUR'), ('ETH', 'EUR'), ('USDC', 'EUR'))


class BybitP2PParser(P2PParser, ABC):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    endpoint: str = API_P2P_BYBIT
    user_agent_browser: str = 'safari'
    connection_type: str = CONNECTION_TYPE_P2P_BYBIT
    need_cookies: bool = True
    cookies_names: Tuple[str] = None
    page: int = 1
    rows: int = 1
    fake_useragent: bool = True
    custom_user_agent: Tuple[str] = (
        'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; pt-pt) AppleWebKit/418.9.1 '
        '(KHTML, like Gecko) Safari/419.3',
    )
    # custom_settings
    fiat_for_amount: str = 'USD'
    min_amount: int = 100
    base_exchange_name: str = 'Wise'

    def __get_min_amount(self, fiat: str) -> str:
        if fiat == self.fiat_for_amount:
            return str(self.min_amount)
        target_exchange = BanksExchangeRates.objects.filter(
            bank__name=self.base_exchange_name, from_fiat=self.fiat_for_amount,
            to_fiat=fiat
        )
        if target_exchange.exists():
            return str(int(target_exchange.get().price * self.min_amount))
        return ''

    def _check_supports_fiat(self, _) -> bool:
        return True

    def _create_body(self, asset: str, fiat: str, trade_type: str) -> dict:
        if trade_type == 'SELL':
            side = '0'
        else:
            side = '1'
        amount = self.__get_min_amount(fiat)
        return {
            "userId": "",
            "size": str(self.rows),
            "page": str(self.page),
            "tokenId": asset,
            "side": side,
            "currencyId": fiat,
            "payment": [self.bank.bybit_name],
            "amount": amount
        }

    @staticmethod
    def _extract_price_from_json(json_data: dict) -> float or None:
        result = json_data['result']
        items = result['items']
        count = result['count']
        if count == 0:
            return None
        first_item = items[0]
        return float(first_item['price'])


class BybitCryptoParser(CryptoExchangesParser):
    crypto_exchange_name: str = CRYPTO_EXCHANGES_NAME
    endpoint: str = API_BYBIT_CRYPTO
    connection_type: str = CONNECTION_TYPE_BYBIT_CRYPTO
    need_cookies: bool = False
    fake_useragent: bool = False
    name_from: str = 'symbol'
    base_spot_fee: float = 0.1
    zero_fees: dict = BYBIT_SPOT_ZERO_FEES

    @staticmethod
    def _extract_price_from_json(json_data: dict) -> float:
        result = json_data['result']
        return float(result['price'])
