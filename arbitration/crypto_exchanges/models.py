from django.db import models

from banks.models import Banks, BanksExchangeRates, BestBankExchanges
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


class Card2Wallet2CryptoExchangesUpdates(UpdatesModel):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='card_2_wallet_2_crypto_exchanges_update',
        on_delete=models.CASCADE
    )


class Card2Wallet2CryptoExchanges(models.Model):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='card_2_wallet_2_crypto_exchanges',
        on_delete=models.CASCADE
    )
    asset = models.CharField(max_length=4)
    fiat = models.CharField(max_length=3)
    trade_type = models.CharField(max_length=4)
    transaction_method = models.CharField(max_length=35)
    transaction_fee = models.FloatField(null=True, blank=True, default=None)
    price = models.FloatField(null=True, blank=True, default=None)
    intra_crypto_exchange = models.ForeignKey(
        IntraCryptoExchanges, related_name='card_2_wallet_2_crypto_exchange',
        on_delete=models.CASCADE
    )
    update = models.ForeignKey(Card2Wallet2CryptoExchangesUpdates,
                               related_name='datas', on_delete=models.CASCADE)


class Card2CryptoExchangesUpdates(UpdatesModel):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='card_2_crypto_exchanges_update',
        on_delete=models.CASCADE
    )


class Card2CryptoExchanges(models.Model):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='card_2_crypto_exchanges',
        on_delete=models.CASCADE
    )
    asset = models.CharField(max_length=4)
    fiat = models.CharField(max_length=3)
    trade_type = models.CharField(max_length=4)
    price = models.FloatField(null=True, blank=True, default=None)
    pre_price = models.FloatField(null=True, blank=True, default=None)
    commission = models.FloatField(null=True, blank=True, default=None)
    update = models.ForeignKey(Card2CryptoExchangesUpdates,
                               related_name='datas', on_delete=models.CASCADE)


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


class BestPaymentChannelsUpdates(UpdatesModel):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='best_payment_channel_update',
        on_delete=models.CASCADE
    )


class BestPaymentChannels(models.Model):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='best_payment_channel',
        on_delete=models.CASCADE
    )
    bank = models.ForeignKey(
        Banks, related_name='best_payment_channel',
        on_delete=models.CASCADE
    )
    asset = models.CharField(max_length=4)
    fiat = models.CharField(max_length=3)
    trade_type = models.CharField(max_length=4)
    price = models.FloatField(null=True, blank=True, default=None)
    payment_channel_model = models.CharField(max_length=30)
    exchange_id = models.PositiveSmallIntegerField()
    update = models.ForeignKey(
        BestPaymentChannelsUpdates, related_name='datas',
        on_delete=models.CASCADE
    )


class BestCombinationPaymentChannelsUpdates(UpdatesModel):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges,
        related_name='best_combinations_payment_channels_update',
        on_delete=models.CASCADE
    )


class BestCombinationPaymentChannels(models.Model):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='best_combinations_payment_channels',
        on_delete=models.CASCADE
    )
    input_bank = models.ForeignKey(
        Banks, related_name='input_bank_best_combinations_payment_channels',
        on_delete=models.CASCADE
    )
    output_bank = models.ForeignKey(
        Banks, related_name='output_bank_best_combinations_payment_channels',
        on_delete=models.CASCADE
    )
    input_exchange = models.ForeignKey(
        BestPaymentChannels,
        related_name='input_exchange_best_combinations_payment_channels',
        on_delete=models.CASCADE
    )
    interim_exchange = models.ForeignKey(
        IntraCryptoExchanges,
        related_name='interim_exchange_best_combinations_payment_channels',
        blank=True, null=True, on_delete=models.CASCADE
    )
    output_exchange = models.ForeignKey(
        BestPaymentChannels,
        related_name='output_exchange_best_combinations_payment_channels',
        on_delete=models.CASCADE
    )
    from_fiat = models.CharField(max_length=3)
    to_fiat = models.CharField(max_length=3)
    price = models.FloatField(null=True, blank=True, default=None)
    update = models.ForeignKey(
        BestCombinationPaymentChannelsUpdates, related_name='datas',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('from_fiat', 'to_fiat', 'input_bank', 'output_bank',
                        'crypto_exchange'),
                name='unique_currency_pair'
            )
        ]


class InterBankAndCryptoExchangesUpdates(UpdatesModel):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges,
        related_name='inter_bank_and_crypro_exchanges_update',
        on_delete=models.CASCADE
    )


class InterBankAndCryptoExchanges(models.Model):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='inter_bank_and_crypro_exchanges',
        on_delete=models.CASCADE
    )
    bank = models.ForeignKey(
        Banks, related_name='inter_bank_and_crypro_exchanges',
        on_delete=models.CASCADE
    )
    crypto_rate = models.ForeignKey(
        BestCombinationPaymentChannels,
        related_name='crypto_rates_inter_bank_and_crypro_exchanges',
        on_delete=models.CASCADE
    )
    bank_rate = models.ForeignKey(
        BestBankExchanges,
        related_name='bank_rate_inter_bank_and_crypro_exchanges',
        on_delete=models.CASCADE, null=True, blank=True, default=None
    )
    list_bank_rate = models.JSONField(null=True, blank=True)
    list_crypto_rate = models.JSONField()
    marginality_percentage = models.FloatField(
        null=True, blank=True, default=None
    )
    update = models.ForeignKey(
        InterBankAndCryptoExchangesUpdates, related_name='datas',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['-marginality_percentage']


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
    diagram = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        ordering = ['-marginality_percentage']


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
