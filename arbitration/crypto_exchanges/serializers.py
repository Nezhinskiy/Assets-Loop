from rest_framework import serializers

from crypto_exchanges.models import InterExchanges, CryptoExchanges, P2PCryptoExchangesRates, IntraCryptoExchanges, InterExchangesUpdates

from banks.models import Banks, BanksExchangeRates, CurrencyMarkets
import decimal

ROUND_TO = 10


class RoundingDecimalField(serializers.DecimalField):
    def validate_precision(self, value):
        return value

    def quantize(self, value):
        """
        Quantize the decimal value to the configured precision.
        """
        if self.decimal_places is None:
            if len(str(value)) - 1 < self.max_digits:
                return value
            length = len(str(int(value)))
            if length > 1:
                self.max_digits -= 3
            round_length = (self.max_digits - length
                            if self.max_digits > length else 1)
            return round(value, round_length)

        context = decimal.getcontext().copy()
        if self.max_digits is not None:
            context.prec = self.max_digits
        return value.quantize(
            decimal.Decimal('.1') ** self.decimal_places,
            rounding=self.rounding,
            context=context
        )


class CryptoExchangesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoExchanges
        fields = ('name',)


class BanksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banks
        fields = ('name',)


class IntraCryptoExchangesSerializer(serializers.ModelSerializer):
    price = RoundingDecimalField(max_digits=ROUND_TO, decimal_places=None)

    class Meta:
        model = IntraCryptoExchanges
        exclude = ['id', 'update', 'crypto_exchange']


class P2PCryptoExchangesRatesSerializer(serializers.ModelSerializer):
    intra_crypto_exchange = IntraCryptoExchangesSerializer(read_only=True)
    price = RoundingDecimalField(max_digits=ROUND_TO, decimal_places=None)

    class Meta:
        model = P2PCryptoExchangesRates
        exclude = [
            'id', 'update', 'trade_type', 'crypto_exchange', 'bank'
        ]


class CurrencyMarketsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyMarkets
        fields = ('name',)


class BanksExchangeRatesSerializer(serializers.ModelSerializer):
    bank = BanksSerializer(read_only=True)
    currency_market = CurrencyMarketsSerializer(read_only=True)
    price = RoundingDecimalField(max_digits=ROUND_TO, decimal_places=None)

    class Meta:
        model = BanksExchangeRates
        exclude = ['id', 'update']


class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterExchangesUpdates
        fields = ('updated',)


class InterExchangesSerializer(serializers.ModelSerializer):
    crypto_exchange = CryptoExchangesSerializer(read_only=True)
    input_bank = BanksSerializer(read_only=True)
    output_bank = BanksSerializer(read_only=True)
    input_crypto_exchange = P2PCryptoExchangesRatesSerializer(read_only=True)
    output_crypto_exchange = P2PCryptoExchangesRatesSerializer(read_only=True)
    interim_crypto_exchange = IntraCryptoExchangesSerializer(read_only=True)
    second_interim_crypto_exchange = IntraCryptoExchangesSerializer(
        read_only=True)
    bank_exchange = BanksExchangeRatesSerializer(read_only=True)
    marginality_percentage = RoundingDecimalField(max_digits=4,
                                                  decimal_places=2)
    update = UpdateSerializer(read_only=True)

    class Meta:
        model = InterExchanges
        fields = '__all__'
