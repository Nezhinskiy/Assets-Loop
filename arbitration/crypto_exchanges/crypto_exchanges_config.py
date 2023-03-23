from collections import OrderedDict

from banks.banks_config import BANKS_CONFIG
from crypto_exchanges.crypto_exchanges_registration.binance import (
    BINANCE_ASSETS, BINANCE_ASSETS_FOR_FIAT, BINANCE_CRYPTO_FIATS,
    BINANCE_DEPOSIT_FIATS, BINANCE_INVALID_PARAMS_LIST, BINANCE_WITHDRAW_FIATS)
from crypto_exchanges.crypto_exchanges_registration.bybit import (
    BYBIT_ASSETS, BYBIT_ASSETS_FOR_FIAT, BYBIT_CRYPTO_FIATS,
    BYBIT_INVALID_PARAMS_LIST)

TRADE_TYPES = ('BUY', 'SELL')

CRYPTO_EXCHANGES_CONFIG = {
    'Binance': {
        'assets': BINANCE_ASSETS,
        'assets_for_fiats': BINANCE_ASSETS_FOR_FIAT,
        'invalid_params_list': BINANCE_INVALID_PARAMS_LIST,
        'crypto_fiats': BINANCE_CRYPTO_FIATS,
        'deposit_fiats': BINANCE_DEPOSIT_FIATS,
        'withdraw_fiats': BINANCE_WITHDRAW_FIATS,
    },
    'Bybit': {
        'assets': BYBIT_ASSETS,
        'assets_for_fiats': BYBIT_ASSETS_FOR_FIAT,
        'invalid_params_list': BYBIT_INVALID_PARAMS_LIST,
        'crypto_fiats': BYBIT_CRYPTO_FIATS,

    }
}
ALL_FIATS = tuple(
    OrderedDict.fromkeys(
        fiat for bank_info in BANKS_CONFIG.values()
        for fiat in bank_info['currencies']
    )
)
ALL_ASSETS = tuple(
    OrderedDict.fromkeys(
        asset for crypto_exchange_info in CRYPTO_EXCHANGES_CONFIG.values()
        for asset in crypto_exchange_info['assets']
    )
)
