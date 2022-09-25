from banks.banks_registration.tinkoff import (
    TINKOFF_CURRENCIES, TINKOFF_CURRENCIES_WITH_REQUISITES, IntraTinkoff,
    TinkoffParser)
from banks.banks_registration.wise import (WISE_CURRENCIES, IntraWise,
                                           WiseParser)
from crypto_exchanges.models import (Card2CryptoExchanges,
                                     Card2Wallet2CryptoExchanges,
                                     P2PCryptoExchangesRates)
from banks.models import BanksExchangeRates, IntraBanksNotLoopedExchanges, BestBankExchanges

BANKS_CONFIG = {
    'Tinkoff': {
        'bank_parser': TinkoffParser,
        'intra_exchange': IntraTinkoff,
        'currencies': TINKOFF_CURRENCIES,
        'currencies_with_requisites': TINKOFF_CURRENCIES_WITH_REQUISITES,
        'crypto_exchanges': ('Binance',),
        'payment_channels': (
            P2PCryptoExchangesRates,
        ),
        'bank_invest_exchanges': ['Tinkoff']
    },
    'Wise': {
        'bank_parser': WiseParser,
        'intra_exchange': IntraWise,
        'currencies': WISE_CURRENCIES,
        'payment_channels': (
            Card2CryptoExchanges, Card2Wallet2CryptoExchanges,
            P2PCryptoExchangesRates
        ),
        'bank_invest_exchanges': []
    }
}
