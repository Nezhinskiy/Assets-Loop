from itertools import product

from banks.banks_config import BANKS_CONFIG
from banks.models import IntraBanksExchanges
from crypto_exchanges.crypto_exchanges_config import CRYPTO_EXCHANGES_CONFIG
from crypto_exchanges.models import (IntraCryptoExchanges,
                                     P2PCryptoExchangesRates)

FIATS = ('RUB', 'USD', 'EUR')

class InterExchanges(object):
    currencies_with_requisites = None
    percentage_round_to = 2

    def main_loop(self, input_bank_margin_exchanges_list, output_bank_margin_exchanges_list):
        for input_bank_name, input_bank_config in BANKS_CONFIG:
            # margin_exchanges
            input_bank_margin_exchanges = IntraBanksExchanges.objects.filter(
                bank__name=input_bank_name, marginality_percentage__gt=0
            )
            if input_bank_margin_exchanges.exists():
                for input_bank_margin_exchange in input_bank_margin_exchanges:
                    input_bank_margin_exchanges_list.append(input_bank_margin_exchange)
            # margin_exchanges_end
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
                        pay_type=input_bank_name
                    )
                    p2p_instant_input_price = target_p2p_instant_input.price
                    target_p2p_slow_input = P2PCryptoExchangesRates.objects.get(
                        assets=input_asset, fiat=input_currency, trade_type='SELL',
                        pay_type=input_bank_name
                    )
                    p2p_slow_input_price = target_p2p_slow_input.price
                    # crypto enter loop end
                    # crypto intra loop start
                    intra_crypto_exchanges = IntraCryptoExchanges.objects.filter(
                        from_asset=input_asset)
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
                                    trade_type='SELL',
                                    pay_type=output_bank_name
                                )
                                p2p_instant_output_price = target_p2p_instant_output.price
                                target_p2p_slow_output = P2PCryptoExchangesRates.objects.get(
                                    assets=output_asset, fiat=output_currency,
                                    trade_type='BUY',
                                    pay_type=output_bank_name
                                )
                                p2p_slow_output_price = target_p2p_slow_input.price
                                # crypto output loop end
                                # margin_exchanges
                                output_bank_margin_exchanges = IntraBanksExchanges.objects.filter(
                                    bank__name=output_bank_name,
                                    marginality_percentage__gt=0
                                )
                                if output_bank_margin_exchanges.exists():
                                    for output_bank_margin_exchange in output_bank_margin_exchanges:
                                        output_bank_margin_exchanges_list.append(
                                            output_bank_margin_exchange)
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

