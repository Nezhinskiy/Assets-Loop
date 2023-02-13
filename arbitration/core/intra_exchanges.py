import math
import sys
from datetime import datetime, timedelta, timezone
from itertools import permutations, product

from django.core.exceptions import MultipleObjectsReturned

from banks.models import Banks, BanksExchangeRates, CurrencyMarkets
from crypto_exchanges.models import (CryptoExchanges, InterExchanges,
                                     InterExchangesUpdates,
                                     IntraCryptoExchanges,
                                     P2PCryptoExchangesRates,
                                     RelatedMarginalityPercentages)


def get_related_exchange(meta_exchange):
    if meta_exchange:
        try:
            model = meta_exchange.payment_channel_model
        except AttributeError:
            model = meta_exchange.bank_exchange_model
        exchange_id = meta_exchange.exchange_id
        return getattr(sys.modules[__name__], model).objects.get(
            id=exchange_id
        )


class InterSimplExchangesCalculate(object):
    crypto_exchange_name = None
    bank_name = None
    simpl = None

    def __init__(self):
        self.crypto_exchange = CryptoExchanges.objects.get(
            name=self.crypto_exchange_name
        )
        self.bank = Banks.objects.get(name=self.bank_name)
        self.update_time = datetime.now(timezone.utc) - timedelta(minutes=10)

    def get_complex_interbank_exchange(self, new_update, records_to_update):
        from banks.banks_config import BANKS_CONFIG
        banks = BANKS_CONFIG.keys()
        input_bank_config = BANKS_CONFIG.get(self.bank_name)
        all_input_fiats = input_bank_config.get('currencies')
        for output_bank_name in banks:
            output_bank = Banks.objects.get(name=output_bank_name)
            output_bank_config = BANKS_CONFIG.get(output_bank_name)
            all_output_fiats = output_bank_config.get('currencies')
            for input_fiat, output_fiat in product(
                    all_input_fiats, all_output_fiats
            ):
                if input_fiat == output_fiat:
                    continue
                bank_exchanges = BanksExchangeRates.objects.filter(
                    bank__in=[self.bank, output_bank],
                    from_fiat=output_fiat, to_fiat=input_fiat,
                    price__isnull=False, update__updated__gte=self.update_time
                )
                input_crypto_exchanges = (
                    P2PCryptoExchangesRates.objects.filter(
                        crypto_exchange=self.crypto_exchange, bank=self.bank,
                        trade_type='BUY', fiat=input_fiat, price__isnull=False,
                        update__updated__gte=self.update_time
                    )
                )
                output_crypto_exchanges = (
                    P2PCryptoExchangesRates.objects.filter(
                        crypto_exchange=self.crypto_exchange, bank=output_bank,
                        trade_type='SELL', fiat=output_fiat,
                        price__isnull=False,
                        update__updated__gte=self.update_time
                    )
                )
                for input_crypto_exchange, output_crypto_exchange in product(
                        input_crypto_exchanges, output_crypto_exchanges
                ):
                    if (
                            input_crypto_exchange.asset
                            != output_crypto_exchange.asset
                    ):
                        target_interim_exchange = (
                            IntraCryptoExchanges.objects.filter(
                                crypto_exchange=self.crypto_exchange,
                                from_asset=input_crypto_exchange.asset,
                                to_asset=output_crypto_exchange.asset,
                                update__updated__gte=self.update_time
                            )
                        )
                        second_interim_crypto_exchange = None
                        if target_interim_exchange.exists():
                            interim_crypto_exchange = (
                                target_interim_exchange.get()
                            )
                        else:
                            target_interim_crypto_exchange = (
                                IntraCryptoExchanges.objects.filter(
                                    crypto_exchange=self.crypto_exchange,
                                    from_asset=input_crypto_exchange.asset,
                                    to_asset='USDT',
                                    update__updated__gte=self.update_time
                                )
                            )
                            target_second_interim_crypto_exchange = (
                                IntraCryptoExchanges.objects.filter(
                                    crypto_exchange=self.crypto_exchange,
                                    from_asset='USDT',
                                    to_asset=output_crypto_exchange.asset,
                                    update__updated__gte=self.update_time
                                )
                            )
                            if (
                                    target_interim_crypto_exchange.exists() and
                                    target_second_interim_crypto_exchange.exists()
                            ):
                                interim_crypto_exchange = (
                                    target_interim_crypto_exchange.get()
                                )
                                second_interim_crypto_exchange = (
                                    target_second_interim_crypto_exchange.get()
                                )
                            else:
                                continue
                    else:
                        interim_crypto_exchange = None
                        second_interim_crypto_exchange = None
                    for bank_exchange in bank_exchanges:
                        marginality_percentage = (
                            self.calculate_marginality_percentage(
                                input_crypto_exchange, interim_crypto_exchange,
                                second_interim_crypto_exchange,
                                output_crypto_exchange, bank_exchange
                            )
                        )

                        self.add_to_bulk_update_or_create_and_bulk_create(
                            new_update, records_to_update,
                            output_bank, input_crypto_exchange,
                            interim_crypto_exchange,
                            second_interim_crypto_exchange,
                            output_crypto_exchange, bank_exchange,
                            marginality_percentage
                        )

    def get_simpl_inter_exchanges(self, new_update, records_to_update):
        from banks.banks_config import BANKS_CONFIG
        banks = BANKS_CONFIG.keys()
        input_bank_config = BANKS_CONFIG.get(self.bank_name)
        all_input_fiats = input_bank_config.get('currencies')
        bank_exchange = None
        for output_bank_name in banks:
            output_bank = Banks.objects.get(name=output_bank_name)
            output_bank_config = BANKS_CONFIG.get(output_bank_name)
            all_output_fiats = output_bank_config.get('currencies')
            for fiat in all_input_fiats:
                if fiat not in all_output_fiats:
                    continue
                input_crypto_exchanges = (
                    P2PCryptoExchangesRates.objects.filter(
                        crypto_exchange=self.crypto_exchange, bank=self.bank,
                        trade_type='BUY', fiat=fiat, price__isnull=False,
                        update__updated__gte=self.update_time
                    )
                )
                output_crypto_exchanges = (
                    P2PCryptoExchangesRates.objects.filter(
                        crypto_exchange=self.crypto_exchange, bank=output_bank,
                        trade_type='SELL', fiat=fiat, price__isnull=False,
                        update__updated__gte=self.update_time
                    )
                )

                for input_crypto_exchange, output_crypto_exchange in product(
                    input_crypto_exchanges, output_crypto_exchanges
                ):
                    if (
                            input_crypto_exchange.asset
                            != output_crypto_exchange.asset
                    ):
                        target_interim_exchange = (
                            IntraCryptoExchanges.objects.filter(
                                crypto_exchange=self.crypto_exchange,
                                from_asset=input_crypto_exchange.asset,
                                to_asset=output_crypto_exchange.asset,
                                update__updated__gte=self.update_time
                            )
                        )
                        second_interim_crypto_exchange = None
                        if target_interim_exchange.exists():
                            interim_crypto_exchange = (
                                target_interim_exchange.get()
                            )
                        else:
                            target_interim_crypto_exchange = (
                                IntraCryptoExchanges.objects.filter(
                                    crypto_exchange=self.crypto_exchange,
                                    from_asset=input_crypto_exchange.asset,
                                    to_asset='USDT',
                                    update__updated__gte=self.update_time
                                )
                            )
                            target_second_interim_crypto_exchange = (
                                IntraCryptoExchanges.objects.filter(
                                    crypto_exchange=self.crypto_exchange,
                                    from_asset='USDT',
                                    to_asset=output_crypto_exchange.asset,
                                    update__updated__gte=self.update_time
                                )
                            )
                            if (target_interim_crypto_exchange.exists() and
                                    target_second_interim_crypto_exchange.exists()):
                                interim_crypto_exchange = (
                                    target_interim_crypto_exchange.get()
                                )
                                second_interim_crypto_exchange = (
                                    target_second_interim_crypto_exchange.get()
                                )
                            else:
                                continue
                    else:
                        interim_crypto_exchange = None
                        second_interim_crypto_exchange = None
                    marginality_percentage = (
                        self.calculate_marginality_percentage(
                            input_crypto_exchange, interim_crypto_exchange,
                            second_interim_crypto_exchange,
                            output_crypto_exchange, bank_exchange
                        )
                    )
                    if marginality_percentage is None:
                        continue
                    self.add_to_bulk_update_or_create_and_bulk_create(
                        new_update, records_to_update,
                        output_bank, input_crypto_exchange,
                        interim_crypto_exchange,
                        second_interim_crypto_exchange, output_crypto_exchange,
                        bank_exchange, marginality_percentage
                    )

    def calculate_marginality_percentage(
            self, input_crypto_exchange, interim_crypto_exchange,
            second_interim_crypto_exchange, output_crypto_exchange,
            bank_exchange
    ):
        if (input_crypto_exchange.price is None
                or output_crypto_exchange.price is None):
            return
        if interim_crypto_exchange is None:
            interim_crypto_exchange_price = 1
        else:
            interim_crypto_exchange_price = interim_crypto_exchange.price
        if second_interim_crypto_exchange is None:
            second_interim_crypto_exchange_price = 1
        else:
            second_interim_crypto_exchange_price = (
                second_interim_crypto_exchange.price)
        bank_exchange_price = (bank_exchange.price if bank_exchange else 1)
        marginality_percentage = (
             input_crypto_exchange.price * interim_crypto_exchange_price
             * second_interim_crypto_exchange_price
             * output_crypto_exchange.price * bank_exchange_price - 1
        ) * 100
        return round(marginality_percentage, 3)

    def create_diagram(self, bank_exchange, input_crypto_exchange,
                       interim_crypto_exchange, second_interim_crypto_exchange,
                       output_bank, output_crypto_exchange):
        diagram = ''
        if bank_exchange and self.bank == bank_exchange.bank:
            if bank_exchange.currency_market:
                diagram += f'{bank_exchange.currency_market.name} '
            else:
                diagram += f'{self.bank.name} '
            diagram += f'{bank_exchange.from_fiat} ⇨ '
        diagram += (f'{self.bank.name} {input_crypto_exchange.fiat} ⇨ '
                    f'{input_crypto_exchange.asset} ⇨ ')
        if interim_crypto_exchange:
            diagram += f'{interim_crypto_exchange.to_asset} ⇨ '
            if second_interim_crypto_exchange:
                diagram += f'{second_interim_crypto_exchange.to_asset} ⇨ '
        diagram += f'{output_bank.name} {output_crypto_exchange.fiat}'
        if (bank_exchange and output_bank == bank_exchange.bank
                and self.bank != output_bank):
            if bank_exchange.currency_market:
                diagram += f' ⇨ {bank_exchange.currency_market.name} '
            else:
                diagram += f' ⇨ {output_bank.name} '
            diagram += f'{bank_exchange.to_fiat}'
        return diagram

    def add_to_bulk_update_or_create_and_bulk_create(
            self, new_update, records_to_update,
            output_bank, input_crypto_exchange, interim_crypto_exchange,
            second_interim_crypto_exchange, output_crypto_exchange,
            bank_exchange, marginality_percentage
    ):
        target_object = InterExchanges.objects.filter(
            crypto_exchange=self.crypto_exchange, input_bank=self.bank,
            output_bank=output_bank,
            input_crypto_exchange=input_crypto_exchange,
            interim_crypto_exchange=interim_crypto_exchange,
            second_interim_crypto_exchange=second_interim_crypto_exchange,
            output_crypto_exchange=output_crypto_exchange,
            bank_exchange=bank_exchange
        )
        if target_object.exists():
            inter_exchange = target_object.get()
            inter_exchange.marginality_percentage = marginality_percentage
            inter_exchange.update = new_update
            records_to_update.append(inter_exchange)
        else:
            InterExchanges.objects.create(
                crypto_exchange=self.crypto_exchange, input_bank=self.bank,
                output_bank=output_bank,
                input_crypto_exchange=input_crypto_exchange,
                interim_crypto_exchange=interim_crypto_exchange,
                second_interim_crypto_exchange=second_interim_crypto_exchange,
                output_crypto_exchange=output_crypto_exchange,
                bank_exchange=bank_exchange,
                marginality_percentage=marginality_percentage,
                diagram=self.create_diagram(
                    bank_exchange, input_crypto_exchange,
                    interim_crypto_exchange, second_interim_crypto_exchange,
                    output_bank, output_crypto_exchange
                ),
                update=new_update
            )
        # related_marginality_percentage = RelatedMarginalityPercentages(
        #     marginality_percentage=marginality_percentage,
        #     inter_exchange=inter_exchange
        # )
        # records_to_create.append(related_marginality_percentage)

    def main(self):
        start_time = datetime.now()
        new_update = InterExchangesUpdates.objects.create(
            crypto_exchange=self.crypto_exchange, bank=self.bank
        )
        records_to_update = []
        if self.simpl:
            self.get_simpl_inter_exchanges(new_update, records_to_update)
        else:
            self.get_complex_interbank_exchange(
                new_update, records_to_update
            )
        InterExchanges.objects.bulk_update(
            records_to_update, ['marginality_percentage', 'update']
        )
        # RelatedMarginalityPercentages.objects.bulk_create(
        #     records_to_create
        # )
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()
