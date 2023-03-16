from django.db import models

from arbitration.settings import FIAT_LENGTH, NAME_LENGTH
from core.models import UpdatesModel


class Banks(models.Model):
    """
    Model to represent banks.
    """
    name = models.CharField(
        max_length=NAME_LENGTH,
        null=True,
        blank=True
    )
    binance_name = models.CharField(
        max_length=NAME_LENGTH,
        null=True,
        blank=True
    )
    bybit_name = models.CharField(
        max_length=NAME_LENGTH,
        null=True,
        blank=True
    )


class CurrencyMarkets(models.Model):
    """
    Model to represent currency markets.
    """
    name = models.CharField(max_length=NAME_LENGTH)


class BanksExchangeRatesUpdates(UpdatesModel):
    """
    Model to represent the last update time for bank exchange rates.
    """
    bank = models.ForeignKey(
        Banks,
        related_name='bank_rates_update',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    currency_market = models.ForeignKey(
        CurrencyMarkets,
        related_name='currency_market_rates_update',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )


class BanksExchangeRates(models.Model):
    """
    Model to represent bank exchange rates.
    """
    bank = models.ForeignKey(
        Banks,
        related_name='bank_rates',
        on_delete=models.CASCADE
    )
    currency_market = models.ForeignKey(
        CurrencyMarkets,
        related_name='currency_market_rates',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    from_fiat = models.CharField(max_length=FIAT_LENGTH)
    to_fiat = models.CharField(max_length=FIAT_LENGTH)
    price = models.FloatField()
    update = models.ForeignKey(
        BanksExchangeRatesUpdates,
        related_name='datas',
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
