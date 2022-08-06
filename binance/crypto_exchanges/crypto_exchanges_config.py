from crypto_exchanges.crypto_exchanges_registration.binance import (
    BinanceCryptoParser, BinanceP2PParser)

CRYPTO_EXCHANGES_CONFIG = {
    'Binance': {
        'p2p_parser': BinanceP2PParser,
        'crypto_exchanges_parser': BinanceCryptoParser,
    },
}
