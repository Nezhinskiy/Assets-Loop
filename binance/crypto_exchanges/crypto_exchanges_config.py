from crypto_exchanges.crypto_exchanges_registration.binance import (
    BINANCE_ASSETS, BINANCE_FIATS, BINANCE_PAY_TYPES, BINANCE_TRADE_TYPES,
    BinanceCryptoParser, BinanceP2PParser, BINANCE_CRYPTO_FIATS)

CRYPTO_EXCHANGES_CONFIG = {
    'Binance': {
        'p2p_parser': BinanceP2PParser,
        'crypto_exchanges_parser': BinanceCryptoParser,
        'assets': BINANCE_ASSETS,
        'trade_types': BINANCE_TRADE_TYPES,
        'fiats': BINANCE_FIATS,
        'crypto_fiats': BINANCE_CRYPTO_FIATS,
        'pay_types': BINANCE_PAY_TYPES
    },
}
