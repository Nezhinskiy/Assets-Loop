from django.db import models

from core.models import UpdatesModel


class Banks(models.Model):
    name = models.CharField(max_length=10, null=True, blank=True)
    binance_name = models.CharField(max_length=15, null=True, blank=True)


class CurrencyMarkets(models.Model):
    name = models.CharField(max_length=15)


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
