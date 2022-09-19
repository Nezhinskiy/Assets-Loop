from banks.banks_config import BANKS_CONFIG
from crypto_exchanges.crypto_exchanges_registration.binance import (
    BINANCE_ASSETS, BINANCE_CRYPTO_FIATS, BINANCE_FIATS, BINANCE_PAY_TYPES,
    BINANCE_TRADE_TYPES, DEPOSIT_FIATS, WITHDRAW_FIATS, BinanceCryptoParser,
    BinanceP2PParser)
from crypto_exchanges.models import (Card2CryptoExchanges,
                                     Card2Wallet2CryptoExchanges,
                                     P2PCryptoExchangesRates)

CRYPTO_EXCHANGES_CONFIG = {
    'all_fiats': tuple({fiat for bank_info in BANKS_CONFIG.values()
                        for fiat in bank_info['currencies']}),
    'Binance': {
        'p2p_parser': BinanceP2PParser,
        'crypto_exchanges_parser': BinanceCryptoParser,
        'assets': BINANCE_ASSETS,
        'trade_types': BINANCE_TRADE_TYPES,
        'fiats': BINANCE_FIATS,
        'crypto_fiats': BINANCE_CRYPTO_FIATS,
        'pay_types': BINANCE_PAY_TYPES,
        'deposit_fiats': DEPOSIT_FIATS,
        'withdraw_fiats': WITHDRAW_FIATS,
        'payment_channels': (
            P2PCryptoExchangesRates, Card2CryptoExchanges,
            Card2Wallet2CryptoExchanges
        )


    },
}
