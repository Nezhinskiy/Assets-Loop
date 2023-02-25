from banks.banks_config import BANKS_CONFIG
from banks.currency_markets_registration.tinkoff_invest import \
    CURRENCY_MARKET_NAME
from banks.models import Banks, CurrencyMarkets
from crypto_exchanges.models import CryptoExchanges

from crypto_exchanges.crypto_exchanges_registration.binance import \
    BinanceListsFiatCryptoParser


def banks():
    for bank_name in BANKS_CONFIG.keys():
        if not Banks.objects.filter(name=bank_name).exists():
            binance_name = (
                bank_name if bank_name != 'Tinkoff' else 'TinkoffNew'
            )
            Banks.objects.create(name=bank_name, binance_name=binance_name)


def currency_markets():
    if not CurrencyMarkets.objects.filter(name=CURRENCY_MARKET_NAME
                                          ).exists():
        CurrencyMarkets.objects.create(name=CURRENCY_MARKET_NAME)


def crypto_exchanges():
    from crypto_exchanges.crypto_exchanges_config import \
        CRYPTO_EXCHANGES_CONFIG
    for crypto_exchange_name in list(CRYPTO_EXCHANGES_CONFIG.keys())[1:]:
        if not CryptoExchanges.objects.filter(
                name=crypto_exchange_name
        ).exists():
            CryptoExchanges.objects.create(name=crypto_exchange_name)


def crypto_list():
    binance_fiat_crypto_list_parser = BinanceListsFiatCryptoParser()
    binance_fiat_crypto_list_parser.main()


def all_registration():
    banks()
    currency_markets()
    crypto_exchanges()
    crypto_list()
