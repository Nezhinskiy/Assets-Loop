from binance.models import ExchangeUpdates, BankExchanges

FIATS = (
    ('RUB', 'Rub'),
    ('USD', 'Usd'),
    ('EUR', 'Eur'),
    ('ILS', 'Ils'),
)

class TinkoffUpdates(ExchangeUpdates):

class TinkoffExchanges(BankExchanges):
    FIATS = FIATS
    ExchangeUpdates = TinkoffUpdates
