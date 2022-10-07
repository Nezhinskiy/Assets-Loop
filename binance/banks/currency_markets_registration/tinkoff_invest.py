import os

from banks.models import CurrencyMarkets
from core.parsers import BankInvestParser

CURRENCY_MARKET_NAME = (
    os.path.basename(__file__).split('.')[0].capitalize().replace('_', ' '))


def reg():
    if not CurrencyMarkets.objects.filter(name=CURRENCY_MARKET_NAME
                                          ).exists():
        CurrencyMarkets.objects.create(name=CURRENCY_MARKET_NAME)


def get_tinkoff_invest_exchanges():
    reg()
    endpoint = ('https://www.tinkoff.ru/api/invest-gw/'
                'social/post/feed/v1/post/instrument/')
    link_ends = (
        'USDRUB', 'EURRUB'
    ) # 'GBPRUB', 'HKDRUB', 'TRYRUB', 'KZTRUB_TOM', 'BYNRUB_TOM', 'AMDRUB_TOM' # 'CHFRUB', 'JPYRUB',
    tinkoff_invest_parser = BankInvestParser(
        CURRENCY_MARKET_NAME, endpoint, link_ends
    )
    message = tinkoff_invest_parser.main()
    return message
