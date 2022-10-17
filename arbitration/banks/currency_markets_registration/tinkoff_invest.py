import os

from core.parsers import BankInvestParser

CURRENCY_MARKET_NAME = (
    os.path.basename(__file__).split('.')[0].capitalize().replace('_', ' '))


def get_tinkoff_invest_exchanges():
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
