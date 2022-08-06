from sys import getsizeof

from banks.banks_config import BANKS_CONFIG
from core.parsers import CryptoExchangesParser, P2PParser

CRYPTO_EXCHANGES_NAME = 'Binance'

BINANCE_ASSETS = ()
BINANCE_TRADE_TYPES = ()
BINANCE_FIATS = ()
BINANCE_PAY_TYPES = (pay_type for pay_type in BANKS_CONFIG.values())

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
PAY_TYPES = (
    ('Tinkoff', 'Tinkoff'),
    ('Wise', 'Wise'),
    # 'TBCbank',
    # 'BankofGeorgia',
    ('RosBank', 'RosBank'),
    ('RUBfiatbalance', 'RUBfiatbalance')
)


class BinanceP2PParser(P2PParser):
    crypto_exchanges_name = CRYPTO_EXCHANGES_NAME
    assets = ASSETS
    fiats = FIATS
    pay_types = PAY_TYPES
    trade_types = TRADE_TYPES
    endpoint = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
    page = 1
    rows = 1

    def create_body(self, asset, trade_type, fiat, pay_types):
        return {
            "page": self.page,
            "rows": self.rows,
            "publisherType": None,
            "asset": asset,
            "tradeType": trade_type,
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
    crypto_exchanges_name = CRYPTO_EXCHANGES_NAME
    fiats = ASSETS
    endpoint = 'https://api.binance.com/api/v3/ticker/price?'
    name_from = 'symbol'

    def converts_choices_to_set(self, choices: tuple[tuple[str, str]]
                                ) -> list[str]:
        """repackaging choices into a set."""
        return [choice[0] for choice in choices]

    def extract_price_from_json(self, json_data) -> float:
        price: float = float(json_data['price'])
        return price

    def create_params(self, fiats_combinations):
        params = [
            dict([(self.name_from, ''.join([params[0], params[-1]]))])
            for params in fiats_combinations
        ]
        return params

    def calculates_buy_and_sell_data(self, params) -> tuple[dict, dict]:
        price = self.extract_price_from_json(self.get_api_answer(params))
        for from_fiat in self.converts_choices_to_set(self.fiats):
            if from_fiat in params['symbol'][0:4]:
                for to_fiat in self.converts_choices_to_set(self.fiats):
                    if to_fiat in params['symbol'][-4:]:
                        buy_data = {
                            'from_fiat': from_fiat,
                            'to_fiat': to_fiat,
                            'price': round(price, self.ROUND_TO)
                        }
                        sell_data = {
                            'from_fiat': to_fiat,
                            'to_fiat': from_fiat,
                            'price': round(1.0 / price, self.ROUND_TO)
                        }
                        return buy_data, sell_data


def get_all_binance_crypto_exchanges():
    binance_crypto_parser = BinanceCryptoParser()
    message = binance_crypto_parser.main()
    return message


def get_all_p2p_binance_exchanges():
    binance_parser = BinanceP2PParser()
    message = binance_parser.main()
    return message
