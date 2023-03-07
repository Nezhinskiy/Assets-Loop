from django.db import models

from arbitration.settings import (ASSET_LENGTH, CHANNEL_LENGTH, DIAGRAM_LENGTH,
                                  FIAT_LENGTH, NAME_LENGTH, TRADE_TYPE_LENGTH)
from banks.models import Banks, BanksExchangeRates
from core.models import UpdatesModel


class CryptoExchanges(models.Model):
    """
    Model to represent crypto exchanges.
    """
    name = models.CharField(max_length=NAME_LENGTH)


class IntraCryptoExchangesRatesUpdates(UpdatesModel):
    """
    Model to store the last update date of intra crypto exchange rates.
    """
    crypto_exchange = models.ForeignKey(
        CryptoExchanges,
        related_name='crypto_exchanges_update',
        on_delete=models.CASCADE
    )


class IntraCryptoExchangesRates(models.Model):
    """
    Model to store the intra crypto exchange rates.
    """
    crypto_exchange = models.ForeignKey(
        CryptoExchanges,
        related_name='crypto_exchanges',
        on_delete=models.CASCADE
    )
    from_asset = models.CharField(max_length=ASSET_LENGTH)
    to_asset = models.CharField(max_length=ASSET_LENGTH)
    price = models.FloatField()
    update = models.ForeignKey(
        IntraCryptoExchangesRatesUpdates,
        related_name='datas',
        on_delete=models.CASCADE
    )
    spot_fee = models.FloatField(default=None)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'crypto_exchange', 'from_asset', 'to_asset'
                ), name='unique_intra_crypto_exchanges'
            )
        ]


class CryptoExchangesRatesUpdates(UpdatesModel):
    """
    Model to store the last update date of crypto exchange rates.
    """
    crypto_exchange = models.ForeignKey(
        CryptoExchanges,
        related_name='crypto_exchange_rates_update',
        on_delete=models.CASCADE
    )
    bank = models.ForeignKey(
        Banks,
        related_name='crypto_exchange_rates_update',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    payment_channel = models.CharField(
        max_length=CHANNEL_LENGTH,
        null=True,
        blank=True
    )


class CryptoExchangesRates(models.Model):
    """
    Model to store the crypto exchange rates.
    """
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='crypto_exchange_rates',
        on_delete=models.CASCADE
    )
    asset = models.CharField(max_length=ASSET_LENGTH)
    fiat = models.CharField(max_length=FIAT_LENGTH)
    trade_type = models.CharField(max_length=TRADE_TYPE_LENGTH)
    bank = models.ForeignKey(
        Banks,
        related_name='crypto_exchange_rates',
        on_delete=models.CASCADE
    )
    payment_channel = models.CharField(
        max_length=CHANNEL_LENGTH,
        null=True,
        blank=True
    )
    transaction_method = models.CharField(
        max_length=CHANNEL_LENGTH,
        null=True,
        blank=True
    )
    transaction_fee = models.FloatField(
        null=True,
        blank=True,
        default=None
    )
    price = models.FloatField(
        null=True,
        blank=True,
        default=None
    )
    pre_price = models.FloatField(
        null=True,
        blank=True,
        default=None
    )
    intra_crypto_exchange = models.ForeignKey(
        IntraCryptoExchangesRates,
        related_name='card_2_wallet_2_crypto_exchange_rates',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    update = models.ForeignKey(
        CryptoExchangesRatesUpdates,
        related_name='datas',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'crypto_exchange', 'bank', 'asset', 'trade_type',
                    'fiat', 'transaction_method', 'payment_channel'
                ), name='unique_crypto_exchange_rates'
            )
        ]


class ListsFiatCryptoUpdates(UpdatesModel):
    """
    Model to store the last update date of fiat-crypto pairs lists.
    """
    crypto_exchange = models.ForeignKey(
        CryptoExchanges,
        related_name='list_fiat_crypto_update',
        on_delete=models.CASCADE
    )


class ListsFiatCrypto(models.Model):
    """
    Model to store the list of fiat-crypto pairs for a crypto exchange.
    """
    crypto_exchange = models.ForeignKey(
        CryptoExchanges,
        related_name='list_fiat_crypto',
        on_delete=models.CASCADE
    )
    list_fiat_crypto = models.JSONField()
    trade_type = models.CharField(max_length=TRADE_TYPE_LENGTH)
    update = models.ForeignKey(
        ListsFiatCryptoUpdates,
        related_name='datas',
        on_delete=models.CASCADE
    )


class InterExchangesUpdates(UpdatesModel):
    """
    Model to store the last update date of inter-exchange rates.
    """
    crypto_exchange = models.ForeignKey(
        CryptoExchanges,
        related_name='inter_exchanges_update',
        on_delete=models.CASCADE
    )
    bank = models.ForeignKey(
        Banks,
        related_name='inter_exchanges_update',
        on_delete=models.CASCADE
    )
    full_update = models.BooleanField(default=True)
    international = models.BooleanField(default=True)
    simpl = models.BooleanField(default=True)
    ended = models.BooleanField(default=False)


class InterExchanges(models.Model):
    """
    Model to store the inter-exchange rates for a crypto exchange.
    """
    crypto_exchange = models.ForeignKey(
        CryptoExchanges,
        related_name='inter_exchanges',
        on_delete=models.CASCADE
    )
    input_bank = models.ForeignKey(
        Banks,
        related_name='input_bank_inter_exchanges',
        on_delete=models.CASCADE
    )
    output_bank = models.ForeignKey(
        Banks,
        related_name='output_bank_inter_exchanges',
        on_delete=models.CASCADE
    )
    input_crypto_exchange = models.ForeignKey(
        CryptoExchangesRates,
        related_name='input_crypto_exchange_inter_exchanges',
        on_delete=models.CASCADE
    )
    interim_crypto_exchange = models.ForeignKey(
        IntraCryptoExchangesRates,
        related_name='interim_exchange_inter_exchanges',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    second_interim_crypto_exchange = models.ForeignKey(
        IntraCryptoExchangesRates,
        related_name='second_interim_exchange_inter_exchanges',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    output_crypto_exchange = models.ForeignKey(
        CryptoExchangesRates,
        related_name='output_crypto_exchange_inter_exchanges',
        on_delete=models.CASCADE
    )
    bank_exchange = models.ForeignKey(
        BanksExchangeRates,
        related_name='bank_rate_inter_exchanges',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    marginality_percentage = models.FloatField(
        verbose_name='Marginality percentage'
    )
    diagram = models.CharField(
        max_length=DIAGRAM_LENGTH,
        null=True,
        blank=True
    )
    dynamics = models.CharField(
        max_length=TRADE_TYPE_LENGTH,
        null=True,
        default=None
    )
    new = models.BooleanField(
        null=True,
        default=True
    )
    update = models.ForeignKey(
        InterExchangesUpdates,
        related_name='datas',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['-marginality_percentage']
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'crypto_exchange', 'input_bank', 'output_bank',
                    'input_crypto_exchange', 'interim_crypto_exchange',
                    'second_interim_crypto_exchange', 'output_crypto_exchange',
                    'bank_exchange'
                ), name='unique_inter_exchanges'
            )
        ]


class RelatedMarginalityPercentages(models.Model):
    """
    A model for storing the percentage of margin at the time of each update.
    """
    updated = models.DateTimeField(
        verbose_name='Update date',
        auto_now_add=True,
        db_index=True
    )
    marginality_percentage = models.FloatField(
        verbose_name='Marginality percentage'
    )
    inter_exchange = models.ForeignKey(
        InterExchanges,
        related_name='marginality_percentages',
        on_delete=models.CASCADE
    )
