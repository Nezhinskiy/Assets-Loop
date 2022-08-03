from core.models import BankExchangesModel, ExchangeUpdatesModel
from django.db import models

FIATS_TINKOFF = (
    ('RUB', 'Rub'),
    ('USD', 'Usd'),
    ('EUR', 'Eur'),
    ('ILS', 'Ils'),
    ('GBP', 'Gbp'),
    ('CHF', 'Chf'),
    ('CAD', 'Cad'),
    ('AUD', 'Aud'),
    ('SGD', 'Sgd'),
    ('BGN', 'Bgn'),
    ('BYN', 'Byn'),
    ('AED', 'Aed'),
    ('PLN', 'Pln'),
    ('TRY', 'Try'),
    ('CNY', 'Cny'),
    ('HKD', 'Hkd'),
    ('SEK', 'Sek'),
    ('CZK', 'Czk'),
    ('THB', 'Thb'),
    ('INR', 'Inr'),
    ('JPY', 'Jpy'),
    ('KZT', 'Kzt'),
    ('AMD', 'Amd'),
    ('KRW', 'Krw'),
    ('IDR', 'Idr'),
    ('VND', 'Vnd'),
    ('NOK', 'Nok')
)
FIATS_WISE = (
    ('USD', 'Usd'),
    ('EUR', 'Eur'),
    ('ILS', 'Ils'),
    ('GBP', 'Gbp'),
    ('CHF', 'Chf'),
    ('CAD', 'Cad'),
    ('AUD', 'Aud'),
    ('SGD', 'Sgd'),
    ('BGN', 'Bgn'),
    ('BYN', 'Byn'),
    ('AED', 'Aed'),
    ('PLN', 'Pln'),
    ('TRY', 'Try'),
    ('CNY', 'Cny'),
    ('HKD', 'Hkd'),
    ('SEK', 'Sek'),
    ('CZK', 'Czk'),
    ('THB', 'Thb'),
    ('INR', 'Inr'),
    ('JPY', 'Jpy'),
    ('KZT', 'Kzt'),
    ('AMD', 'Amd'),
    ('KRW', 'Krw'),
    ('IDR', 'Idr'),
    ('VND', 'Vnd'),
    ('NOK', 'Nok'),
)


class TinkoffUpdates(ExchangeUpdatesModel):
    pass


class TinkoffExchanges(BankExchangesModel):
    FIATS = FIATS_TINKOFF
    update = models.ForeignKey(
        TinkoffUpdates, related_name='datas', on_delete=models.CASCADE
    )


class WiseUpdates(ExchangeUpdatesModel):
    pass


class WiseExchanges(BankExchangesModel):
    FIATS = FIATS_WISE
    update = models.ForeignKey(
        WiseUpdates, related_name='datas', on_delete=models.CASCADE
    )
