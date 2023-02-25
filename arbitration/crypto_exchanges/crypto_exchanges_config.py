from collections import OrderedDict

from banks.banks_config import BANKS_CONFIG
from crypto_exchanges.crypto_exchanges_registration.binance import (
    BINANCE_ASSETS, BINANCE_ASSETS_FOR_FIAT, BINANCE_CRYPTO_FIATS,
    BINANCE_FIATS, BINANCE_PAY_TYPES, BINANCE_TRADE_TYPES, DEPOSIT_FIATS,
    INVALID_PARAMS_LIST, WITHDRAW_FIATS, BinanceCryptoParser, BinanceP2PParser)
from crypto_exchanges.models import P2PCryptoExchangesRates

CRYPTO_EXCHANGES_CONFIG = {
    'all_fiats': tuple(
        OrderedDict.fromkeys(
            fiat for bank_info in BANKS_CONFIG.values()
            for fiat in bank_info['currencies']
        )
    ),
    'Binance': {
        'p2p_parser': BinanceP2PParser,
        'crypto_exchanges_parser': BinanceCryptoParser,
        'assets': BINANCE_ASSETS,
        'assets_for_fiats': BINANCE_ASSETS_FOR_FIAT,
        'invalid_params_list': INVALID_PARAMS_LIST,
        'trade_types': BINANCE_TRADE_TYPES,
        'fiats': BINANCE_FIATS,
        'crypto_fiats': BINANCE_CRYPTO_FIATS,
        'pay_types': BINANCE_PAY_TYPES,
        'deposit_fiats': DEPOSIT_FIATS,
        'withdraw_fiats': WITHDRAW_FIATS,
        'payment_channels': (
            P2PCryptoExchangesRates
        )
    },
}
