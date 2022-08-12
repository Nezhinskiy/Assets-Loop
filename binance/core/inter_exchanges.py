import math
from itertools import product

from banks.banks_config import BANKS_CONFIG
from banks.models import IntraBanksExchanges, BanksExchangeRates, IntraBanksNotLoopedExchanges
from crypto_exchanges.crypto_exchanges_config import CRYPTO_EXCHANGES_CONFIG
from crypto_exchanges.models import (IntraCryptoExchanges, InterExchanges,
                                     P2PCryptoExchangesRates)

FIATS = ('RUB', 'USD', 'EUR')

class InterExchangesCalculate(object):
    currencies_with_requisites = None
    percentage_round_to = 2

    def create_list_of_transfers(self, input_currency, input_asset,
                    output_asset, list_of_output_transfers):
        list_of_transfers = [input_currency, input_asset]
        if input_asset != output_asset:
            list_of_transfers.append(output_asset)
        list_of_transfers.append(list_of_output_transfers)
        return list_of_transfers

    def create_marginality_percentage(
            self, p2p_instant_input_price, p2p_slow_input_price,
            intra_crypto_exchange_price, p2p_instant_output_price,
            p2p_slow_output_price, bank_output_price):
        instant_price_tuple = (
            p2p_instant_input_price, intra_crypto_exchange_price,
            p2p_instant_output_price, bank_output_price
        )
        instant_price = math.prod(instant_price_tuple)
        instant_marginality_percentage = instant_price * 100 - 100
        slow_price_tuple = (p2p_slow_input_price, intra_crypto_exchange_price,
                            p2p_slow_output_price, bank_output_price)
        slow_price = math.prod(slow_price_tuple)
        slow_marginality_percentage = slow_price * 100 - 100
        if (instant_marginality_percentage < -5
                and slow_marginality_percentage < -5):
            return False
        return instant_marginality_percentage, slow_marginality_percentage


    def main_loop(self, input_bank_margin_exchanges_list, output_bank_margin_exchanges_list):
        for input_bank_name, input_bank_config in BANKS_CONFIG:
            # crypto enter loop start
            for crypto_exchange_name, crypto_exchange_config in (
                    CRYPTO_EXCHANGES_CONFIG):
                input_currencies_with_requisites = input_bank_config.get(
                    'currencies_with_requisites')
                assets = crypto_exchange_config.get('assets')
                for input_currency, input_asset in product(
                        input_currencies_with_requisites, assets):
                    target_p2p_instant_input = P2PCryptoExchangesRates.objects.get(
                        assets=input_asset, fiat=input_currency, trade_type='BUY',
                        pay_type=input_bank_name, crypto_exchange__name=crypto_exchange_name
                    )
                    p2p_instant_input_price = target_p2p_instant_input.price
                    target_p2p_slow_input = P2PCryptoExchangesRates.objects.get(
                        assets=input_asset, fiat=input_currency, trade_type='SELL',
                        pay_type=input_bank_name, crypto_exchange__name=crypto_exchange_name
                    )
                    p2p_slow_input_price = target_p2p_slow_input.price
                    # crypto enter loop end
                    # crypto intra loop start
                    for count_exchanges in range(2):
                        if count_exchanges == 0:
                            intra_crypto_exchange_price = 1
                            output_asset = input_asset
                        else:
                            intra_crypto_exchanges = IntraCryptoExchanges.objects.filter(
                                from_asset=input_asset,
                                crypto_exchange__name=crypto_exchange_name
                            )
                            for intra_crypto_exchange in intra_crypto_exchanges:
                                intra_crypto_exchange_price = intra_crypto_exchange.price
                                output_asset = intra_crypto_exchange.to_asset
                        # crypto intra loop end
                        # output_bank loop start
                        for output_bank_name, output_bank_config in BANKS_CONFIG:
                            output_currencies_with_requisites = output_bank_config.get(
                                'currencies_with_requisites')
                            for output_currency in output_currencies_with_requisites:
                                # output_bank loop end
                                # crypto output loop start
                                target_p2p_instant_output = P2PCryptoExchangesRates.objects.get(
                                    assets=output_asset, fiat=output_currency,
                                    trade_type='SELL', pay_type=output_bank_name,
                                    crypto_exchange__name=crypto_exchange_name
                                )
                                p2p_instant_output_price = target_p2p_instant_output.price
                                target_p2p_slow_output = P2PCryptoExchangesRates.objects.get(
                                    assets=output_asset, fiat=output_currency,
                                    trade_type='BUY', pay_type=output_bank_name,
                                    crypto_exchange__name=crypto_exchange_name
                                )
                                p2p_slow_output_price = target_p2p_slow_input.price
                                # crypto output loop end
                                # margin_exchanges
                                output_bank_margin_exchanges = IntraBanksNotLoopedExchanges.objects.filter(
                                    bank__name=output_bank_name,
                                    analogous_exchange__from_fiat=output_currency,
                                    analogous_exchange__to_fiat=input_currency,
                                    marginality_percentage__gt=0
                                )
                                if not output_bank_margin_exchanges.exists():
                                    bank_output_exchange = BanksExchangeRates.objects.get(
                                        bank__name=output_bank_name,
                                        from_fiat=output_currency,
                                        to_fiat=input_currency
                                    )
                                    bank_output_price = bank_output_exchange.price
                                    list_of_output_transfers = [output_currency, input_currency]
                                else:
                                    for output_bank_margin_exchange in output_bank_margin_exchanges:
                                        bank_output_price = output_bank_margin_exchange.price
                                        list_of_output_transfers = output_bank_margin_exchange.list_of_transfers
                                        marginality_percentage = self.create_marginality_percentage(
                                            p2p_instant_input_price, p2p_slow_input_price, intra_crypto_exchange_price,
                                            p2p_instant_output_price, p2p_slow_output_price, bank_output_price
                                        )


                                # margin_exchanges_end
                                # bank output loop start





    # def start(self):
    #     for name_of_bank, config_of_bank in self.BANKING_CONFIG:
    #         InsideBankExchanges = config_of_bank['inside_bank_exchanges']
    #         if InsideBankExchanges.object.filter(
    #                 marginality_percentage__gt=0
    #         ).exists():
    #             pass
    #
    # def main(self):

