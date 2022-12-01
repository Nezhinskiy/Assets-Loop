from django.db import models

from core.models import UpdatesModel


class Banks(models.Model):
    name = models.CharField(max_length=10, null=True, blank=True)
    binance_name = models.CharField(max_length=15, null=True, blank=True)


class CurrencyMarkets(models.Model):
    name = models.CharField(max_length=15, null=True, blank=True)


class BanksExchangeRatesUpdates(UpdatesModel):
    bank = models.ForeignKey(
        Banks, related_name='bank_rates_update',
        blank=True, null=True, on_delete=models.CASCADE
    )
    currency_market = models.ForeignKey(
        CurrencyMarkets, related_name='currency_market_rates_update',
        blank=True, null=True, on_delete=models.CASCADE
    )


class BanksExchangeRates(models.Model):
    bank = models.ForeignKey(
        Banks, related_name='bank_rates', on_delete=models.CASCADE
    )
    currency_market = models.ForeignKey(
        CurrencyMarkets, related_name='currency_market_rates',
        blank=True, null=True, on_delete=models.CASCADE
    )
    from_fiat = models.CharField(max_length=3)
    to_fiat = models.CharField(max_length=3)
    price = models.FloatField(null=True, blank=True, default=None)
    update = models.ForeignKey(
        BanksExchangeRatesUpdates, related_name='datas',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'bank', 'from_fiat', 'to_fiat', 'currency_market'
                ),
                name='unique_bank_exchanges'
            )
        ]


class IntraBanksExchangesUpdates(UpdatesModel):
    bank = models.ForeignKey(
        Banks, related_name='bank_exchanges_update', on_delete=models.CASCADE
    )


class IntraBanksExchanges(models.Model):
    bank = models.ForeignKey(
        Banks, related_name='bank_exchanges', on_delete=models.CASCADE
    )
    list_of_transfers = models.JSONField()
    marginality_percentage = models.FloatField(
        null=True, blank=True, default=None
    )
    update = models.ForeignKey(
        IntraBanksExchangesUpdates, related_name='datas',
        on_delete=models.CASCADE
    )


class BankInvestExchangesUpdates(UpdatesModel):
    currency_market = models.ForeignKey(
        CurrencyMarkets, related_name='currency_market_exchanges_update',
        on_delete=models.CASCADE
    )


class BankInvestExchanges(models.Model):
    currency_market = models.ForeignKey(
        CurrencyMarkets, related_name='currency_market_exchanges',
        on_delete=models.CASCADE
    )
    from_fiat = models.CharField(max_length=3)
    to_fiat = models.CharField(max_length=3)
    price = models.FloatField(null=True, blank=True, default=None)
    update = models.ForeignKey(
        BankInvestExchangesUpdates, related_name='datas',
        on_delete=models.CASCADE
    )


class BestBankExchangesUpdates(UpdatesModel):
    pass


class BestBankExchanges(models.Model):
    bank = models.ForeignKey(
        Banks, related_name='best_bank_exchanges',
        on_delete=models.CASCADE
    )
    from_fiat = models.CharField(max_length=3)
    to_fiat = models.CharField(max_length=3)
    price = models.FloatField(null=True, blank=True, default=None)
    bank_exchange_model = models.CharField(max_length=30)
    exchange_id = models.PositiveSmallIntegerField()
    update = models.ForeignKey(
        BestBankExchangesUpdates, related_name='datas',
        on_delete=models.CASCADE
    )
