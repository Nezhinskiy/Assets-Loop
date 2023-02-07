from django.db import models

from banks.models import Banks, BanksExchangeRates
from core.models import UpdatesModel


class CryptoExchanges(models.Model):
    name = models.CharField(max_length=10, null=True, blank=True)


class IntraCryptoExchangesUpdates(UpdatesModel):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='crypto_exchanges_update',
        on_delete=models.CASCADE
    )


class IntraCryptoExchanges(models.Model):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='crypto_exchanges',
        on_delete=models.CASCADE
    )
    from_asset = models.CharField(max_length=4)
    to_asset = models.CharField(max_length=4)
    price = models.FloatField(null=True, blank=True, default=None)
    update = models.ForeignKey(
        IntraCryptoExchangesUpdates, related_name='datas',
        on_delete=models.CASCADE
    )
    spot_fee = models.FloatField(null=True, blank=True, default=None)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'crypto_exchange', 'from_asset', 'to_asset'
                ),
                name='unique_intra_crypto_exchanges'
            )
        ]


class P2PCryptoExchangesRatesUpdates(UpdatesModel):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='p2p_rates_update',
        on_delete=models.CASCADE
    )
    bank = models.ForeignKey(
        Banks, related_name='p2p_rates_update',
        blank=True, null=True, on_delete=models.CASCADE
    )
    payment_channel = models.CharField(max_length=30, null=True, blank=True)


class P2PCryptoExchangesRates(models.Model):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='p2p_rates', on_delete=models.CASCADE
    )
    asset = models.CharField(max_length=4)
    fiat = models.CharField(max_length=3)
    trade_type = models.CharField(max_length=4)
    bank = models.ForeignKey(
        Banks, related_name='p2p_rates', on_delete=models.CASCADE
    )
    price = models.FloatField(null=True, blank=True, default=None)
    payment_channel = models.CharField(max_length=30, null=True, blank=True)
    transaction_method = models.CharField(max_length=35, null=True, blank=True)
    transaction_fee = models.FloatField(null=True, blank=True, default=None)
    pre_price = models.FloatField(null=True, blank=True, default=None)
    intra_crypto_exchange = models.ForeignKey(
        IntraCryptoExchanges,
        related_name='card_2_wallet_2_crypto_exchange_rates',
        blank=True, null=True, on_delete=models.CASCADE
    )
    update = models.ForeignKey(
        P2PCryptoExchangesRatesUpdates, related_name='datas',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'crypto_exchange', 'bank', 'asset', 'trade_type',
                    'fiat', 'transaction_method', 'payment_channel'
                ),
                name='unique_p2p'
            )
        ]


class ListsFiatCryptoUpdates(UpdatesModel):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='list_fiat_crypto_update',
        on_delete=models.CASCADE
    )


class ListsFiatCrypto(models.Model):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='list_fiat_crypto',
        on_delete=models.CASCADE
    )
    list_fiat_crypto = models.JSONField()
    trade_type = models.CharField(max_length=4)
    update = models.ForeignKey(
        ListsFiatCryptoUpdates, related_name='datas', on_delete=models.CASCADE
    )


class InterExchangesUpdates(UpdatesModel):
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


class InterExchanges(models.Model):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='inter_exchanges',
        on_delete=models.CASCADE
    )
    input_bank = models.ForeignKey(
        Banks, related_name='input_bank_inter_exchanges',
        on_delete=models.CASCADE
    )
    output_bank = models.ForeignKey(
        Banks, related_name='output_bank_inter_exchanges',
        on_delete=models.CASCADE
    )
    input_crypto_exchange = models.ForeignKey(
        P2PCryptoExchangesRates,
        related_name='input_crypto_exchange_inter_exchanges',
        on_delete=models.CASCADE
    )
    interim_crypto_exchange = models.ForeignKey(
        IntraCryptoExchanges,
        related_name='interim_exchange_inter_exchanges',
        blank=True, null=True, on_delete=models.CASCADE
    )
    second_interim_crypto_exchange = models.ForeignKey(
        IntraCryptoExchanges,
        related_name='second_interim_exchange_inter_exchanges',
        blank=True, null=True, on_delete=models.CASCADE
    )
    output_crypto_exchange = models.ForeignKey(
        P2PCryptoExchangesRates,
        related_name='output_crypto_exchange_inter_exchanges',
        on_delete=models.CASCADE
    )
    bank_exchange = models.ForeignKey(
        BanksExchangeRates,
        related_name='bank_rate_inter_exchanges',
        blank=True, null=True, on_delete=models.CASCADE
    )
    marginality_percentage = models.FloatField('Marginality percentage')
    update = models.ForeignKey(
        InterExchangesUpdates, related_name='datas',
        on_delete=models.CASCADE
    )
    diagram = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['-marginality_percentage']
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'crypto_exchange', 'input_bank', 'output_bank',
                    'input_crypto_exchange', 'interim_crypto_exchange',
                    'second_interim_crypto_exchange', 'output_crypto_exchange',
                    'bank_exchange'
                ),
                name='unique_inter_exchanges'
            )
        ]


class RelatedMarginalityPercentages(models.Model):
    updated = models.DateTimeField(
        'Update date', auto_now_add=True, db_index=True
    )
    marginality_percentage = models.FloatField()
    inter_exchange = models.ForeignKey(
        InterExchanges,
        related_name='marginality_percentages',
        on_delete=models.CASCADE
    )
