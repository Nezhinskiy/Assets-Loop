from abc import ABC
from datetime import datetime, timedelta, timezone
from itertools import permutations, product
from typing import Tuple, Any

from banks.models import Banks, BanksExchangeRates, CurrencyMarkets
from crypto_exchanges.models import (CryptoExchanges, InterExchanges,
                                     InterExchangesUpdates,
                                     IntraCryptoExchanges,
                                     P2PCryptoExchangesRates,
                                     RelatedMarginalityPercentages)
import logging

from arbitration.settings import BASE_ASSET, \
    DATA_OBSOLETE_IN_MINUTES, ALLOWED_PERCENTAGE, INTER_EXCHANGES_BEGIN_OBSOLETE_MINUTES

from crypto_exchanges.models import P2PCryptoExchangesRatesUpdates


class BaseCalculate(ABC):
    crypto_exchange_name: str

    def __init__(self):
        from banks.banks_config import BANKS_CONFIG
        self.start_time = datetime.now(timezone.utc)
        self.records_to_create = []
        self.records_to_update = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self.crypto_exchange = CryptoExchanges.objects.get(
            name=self.crypto_exchange_name
        )
        self.banks_config = BANKS_CONFIG

    def logger_start(self) -> None:
        message = f'Start {self.__class__.__name__} at {self.start_time}.'
        self.logger.info(message)


class InterExchangesCalculate(BaseCalculate, ABC):
    model = InterExchanges
    model_update = InterExchangesUpdates
    bank_name: str
    simpl: bool
    base_asset: str = BASE_ASSET
    data_obsolete_in_minutes: int = DATA_OBSOLETE_IN_MINUTES
    allowed_percentage: int = ALLOWED_PERCENTAGE
    duration: timedelta

    def __init__(self) -> None:
        super().__init__()
        self.bank = Banks.objects.get(name=self.bank_name)
        self.new_update = self.model_update.objects.create(
            crypto_exchange=self.crypto_exchange, bank=self.bank
        )
        self.banks = self.banks_config.keys()
        self.input_bank_config = self.banks_config.get(self.bank_name)
        self.all_input_fiats = self.input_bank_config.get('currencies')
        self.update_time = datetime.now(timezone.utc) - timedelta(
            minutes=self.data_obsolete_in_minutes
        )
        self.output_bank = None
        self.input_crypto_exchanges = None
        self.output_crypto_exchanges = None

    def logger_end(self) -> None:
        message = (
            f'Finish {self.__class__.__name__} at {self.duration}. Updated: '
            f'{len(self.records_to_update)}'
        )
        self.logger.info(message)

    def filter_input_crypto_exchanges(self, input_fiat: str) -> None:
        self.input_crypto_exchanges = P2PCryptoExchangesRates.objects.filter(
            crypto_exchange=self.crypto_exchange, bank=self.bank,
            trade_type='BUY', fiat=input_fiat, price__isnull=False,
            update__updated__gte=self.update_time
        )

    def filter_output_crypto_exchanges(self, output_fiat: str) -> None:
        self.output_crypto_exchanges = P2PCryptoExchangesRates.objects.filter(
            crypto_exchange=self.crypto_exchange, bank=self.output_bank,
            trade_type='SELL', fiat=output_fiat, price__isnull=False,
            update__updated__gte=self.update_time
        )

    def crypto_exchange_bug_handler(
            self, marginality_percentage, input_crypto_exchange,
            interim_exchange, interim_second_exchange,
            output_crypto_exchange, bank_exchange=None
    ) -> bool:
        if marginality_percentage > self.allowed_percentage:
            diagram = self.create_diagram(
                input_crypto_exchange, interim_exchange,
                interim_second_exchange, self.output_bank,
                output_crypto_exchange, bank_exchange
            )
            message = (
                f'Not allowed percentage due to a bug on the side of the '
                f'crypto exchange. {marginality_percentage}%, {diagram} input '
                f'- {input_crypto_exchange.payment_channel}, output - '
                f'{output_crypto_exchange.payment_channel}.')
            self.logger.warning(message)
            return True
        return False

    def get_two_interim_exchanges(
            self, input_crypto_exchange: P2PCryptoExchangesRates,
            output_crypto_exchange: P2PCryptoExchangesRates
    ) -> tuple[Any, Any]:
        target_interim_exchange = IntraCryptoExchanges.objects.filter(
            crypto_exchange=self.crypto_exchange,
            from_asset=input_crypto_exchange.asset,
            to_asset=output_crypto_exchange.asset,
            update__updated__gte=self.update_time
        )
        if target_interim_exchange.exists():
            return target_interim_exchange.get(), None
        else:
            target_interim_exchange = IntraCryptoExchanges.objects.filter(
                crypto_exchange=self.crypto_exchange,
                from_asset=input_crypto_exchange.asset,
                to_asset=self.base_asset, update__updated__gte=self.update_time
            )
            target_second_interim_exchange = (
                IntraCryptoExchanges.objects.filter(
                    crypto_exchange=self.crypto_exchange,
                    from_asset=self.base_asset,
                    to_asset=output_crypto_exchange.asset,
                    update__updated__gte=self.update_time
                )
            )
            if (target_interim_exchange.exists() and
                    target_second_interim_exchange.exists()):
                return (target_interim_exchange.get(),
                        target_second_interim_exchange.get())
            return None, None

    def get_complex_interbank_exchange(self) -> None:
        for output_bank_name in self.banks:
            self.output_bank = Banks.objects.get(name=output_bank_name)
            output_bank_config = self.banks_config.get(output_bank_name)
            all_output_fiats = output_bank_config.get('currencies')
            for input_fiat, output_fiat in product(
                    self.all_input_fiats, all_output_fiats
            ):
                if input_fiat == output_fiat:
                    continue
                bank_exchanges = BanksExchangeRates.objects.filter(
                    bank__in=[self.bank, self.output_bank],
                    from_fiat=output_fiat, to_fiat=input_fiat,
                    price__isnull=False, update__updated__gte=self.update_time
                )
                self.filter_input_crypto_exchanges(input_fiat)
                self.filter_output_crypto_exchanges(output_fiat)
                for input_crypto_exchange, output_crypto_exchange in product(
                        self.input_crypto_exchanges,
                        self.output_crypto_exchanges
                ):
                    if (input_crypto_exchange.asset
                            != output_crypto_exchange.asset):
                        interim_exchange, interim_second_exchange = (
                            self.get_two_interim_exchanges(
                                input_crypto_exchange, output_crypto_exchange
                            )
                        )
                    else:
                        interim_exchange = None
                        interim_second_exchange = None
                    for bank_exchange in bank_exchanges:
                        marginality_percentage = (
                            self.calculate_marginality_percentage(
                                input_crypto_exchange, interim_exchange,
                                interim_second_exchange,
                                output_crypto_exchange, bank_exchange
                            )
                        )
                        if self.crypto_exchange_bug_handler(
                                marginality_percentage,
                                input_crypto_exchange, interim_exchange,
                                interim_second_exchange,
                                output_crypto_exchange, bank_exchange
                        ):
                            continue
                        self.add_to_bulk_update_or_create_and_bulk_create(
                            input_crypto_exchange, interim_exchange,
                            interim_second_exchange, output_crypto_exchange,
                            marginality_percentage, bank_exchange
                        )

    def get_simpl_inter_exchanges(self) -> None:
        for output_bank_name in self.banks:
            self.output_bank = Banks.objects.get(name=output_bank_name)
            output_bank_config = self.banks_config.get(output_bank_name)
            all_output_fiats = output_bank_config.get('currencies')
            for fiat in self.all_input_fiats:
                if fiat not in all_output_fiats:
                    continue
                self.filter_input_crypto_exchanges(fiat)
                self.filter_output_crypto_exchanges(fiat)
                for input_crypto_exchange, output_crypto_exchange in product(
                        self.input_crypto_exchanges,
                        self.output_crypto_exchanges
                ):
                    if (input_crypto_exchange.asset
                            != output_crypto_exchange.asset):
                        interim_exchange,  interim_second_exchange = (
                            self.get_two_interim_exchanges(
                                input_crypto_exchange, output_crypto_exchange
                            )
                        )
                        if interim_exchange is None:
                            continue
                    else:
                        interim_exchange = None
                        interim_second_exchange = None
                    marginality_percentage = (
                        self.calculate_marginality_percentage(
                            input_crypto_exchange, interim_exchange,
                            interim_second_exchange, output_crypto_exchange
                        )
                    )
                    if self.crypto_exchange_bug_handler(
                            marginality_percentage, input_crypto_exchange,
                            interim_exchange, interim_second_exchange,
                            output_crypto_exchange
                    ):
                        continue
                    self.add_to_bulk_update_or_create_and_bulk_create(
                        input_crypto_exchange, interim_exchange,
                        interim_second_exchange, output_crypto_exchange,
                        marginality_percentage
                    )

    @staticmethod
    def calculate_marginality_percentage(
            input_crypto_exchange, interim_exchange,
            interim_second_exchange, output_crypto_exchange,
            bank_exchange=None
    ) -> float:
        interim_exchange_price = (1 if interim_exchange is None
                                  else interim_exchange.price)
        second_interim_exchange_price = (1 if interim_second_exchange is None
                                         else interim_second_exchange.price)
        bank_exchange_price = (1 if bank_exchange is None
                               else bank_exchange.price)
        marginality_percentage = (
             input_crypto_exchange.price * interim_exchange_price
             * second_interim_exchange_price
             * output_crypto_exchange.price * bank_exchange_price - 1
        ) * 100
        return round(marginality_percentage, 2)

    def create_diagram(
            self, input_crypto_exchange, interim_exchange,
            interim_second_exchange, output_bank,  output_crypto_exchange,
            bank_exchange=None
    ) -> str:
        diagram = ''
        if bank_exchange and self.bank == bank_exchange.bank:
            if bank_exchange.currency_market:
                diagram += f'{bank_exchange.currency_market.name} '
            else:
                diagram += f'{self.bank.name} '
            diagram += f'{bank_exchange.from_fiat} ⇨ '
        diagram += (f'{self.bank.name} {input_crypto_exchange.fiat} ⇨ '
                    f'{input_crypto_exchange.asset} ⇨ ')
        if interim_exchange:
            diagram += f'{interim_exchange.to_asset} ⇨ '
            if interim_second_exchange:
                diagram += f'{interim_second_exchange.to_asset} ⇨ '
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
            self, input_crypto_exchange, interim_exchange,
            interim_second_exchange, output_crypto_exchange,
            marginality_percentage, bank_exchange=None
    ) -> None:
        target_object = self.model.objects.filter(
            crypto_exchange=self.crypto_exchange, input_bank=self.bank,
            output_bank=self.output_bank,
            input_crypto_exchange=input_crypto_exchange,
            interim_crypto_exchange=interim_exchange,
            second_interim_crypto_exchange=interim_second_exchange,
            output_crypto_exchange=output_crypto_exchange,
            bank_exchange=bank_exchange
        )
        if target_object.exists():
            inter_exchange = target_object.get()
            if inter_exchange.marginality_percentage > marginality_percentage:
                inter_exchange.dynamics = 'fall'
            elif (inter_exchange.marginality_percentage
                  < marginality_percentage):
                inter_exchange.dynamics = 'rise'
            else:
                inter_exchange.dynamics = None
            relevance_time = inter_exchange.update.updated + timedelta(
                minutes=INTER_EXCHANGES_BEGIN_OBSOLETE_MINUTES)
            if relevance_time < self.start_time:
                inter_exchange.new = True
            else:
                inter_exchange.new = False
            inter_exchange.marginality_percentage = marginality_percentage
            inter_exchange.update = self.new_update
            self.records_to_update.append(inter_exchange)
        else:
            self.model.objects.create(
                crypto_exchange=self.crypto_exchange, input_bank=self.bank,
                output_bank=self.output_bank,
                input_crypto_exchange=input_crypto_exchange,
                interim_crypto_exchange=interim_exchange,
                second_interim_crypto_exchange=interim_second_exchange,
                output_crypto_exchange=output_crypto_exchange,
                bank_exchange=bank_exchange,
                marginality_percentage=marginality_percentage,
                diagram=self.create_diagram(
                    input_crypto_exchange, interim_exchange,
                    interim_second_exchange, self.output_bank,
                    output_crypto_exchange, bank_exchange
                ), dynamics=None, new=True, update=self.new_update
            )
        # related_marginality_percentage = RelatedMarginalityPercentages(
        #     marginality_percentage=marginality_percentage,
        #     inter_exchange=inter_exchange
        # )
        # records_to_create.append(related_marginality_percentage)

    def main(self) -> None:
        self.logger_start()
        if self.simpl:
            self.get_simpl_inter_exchanges()
        else:
            self.get_complex_interbank_exchange()
        self.model.objects.bulk_update(
            self.records_to_update,
            ['marginality_percentage', 'dynamics', 'new',  'update']
        )
        # RelatedMarginalityPercentages.objects.bulk_create(
        #     self.records_to_create
        # )
        time_now = datetime.now(timezone.utc)
        self.duration = time_now - self.start_time
        self.new_update.updated = time_now
        self.new_update.duration = self.duration
        self.new_update.save()
        self.logger_end()


class Card2Wallet2CryptoExchangesCalculate(BaseCalculate, ABC):
    model = P2PCryptoExchangesRates
    model_update = P2PCryptoExchangesRatesUpdates
    payment_channel = 'Card2Wallet2CryptoExchange'
    data_obsolete_in_minutes: int = DATA_OBSOLETE_IN_MINUTES

    def __init__(self, trade_type: str) -> None:
        super().__init__()
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        self.new_update = self.model_update.objects.create(
            crypto_exchange=self.crypto_exchange,
            payment_channel=self.payment_channel
        )
        self.crypto_exchanges_configs = CRYPTO_EXCHANGES_CONFIG.get(
            self.crypto_exchange_name)
        self.assets = set(self.crypto_exchanges_configs.get('assets'))
        self.trade_type = trade_type
        self.deposit_fiats = self.crypto_exchanges_configs.get('deposit_fiats')
        self.withdraw_fiats = self.crypto_exchanges_configs.get(
            'withdraw_fiats')
        self.invalid_params_list = self.crypto_exchanges_configs.get(
            'invalid_params_list')
        self.update_time = datetime.now(timezone.utc) - timedelta(
            minutes=self.data_obsolete_in_minutes
        )
        self.duration = None

    def logger_end(self) -> None:
        message = f'Finish {self.__class__.__name__} at {self.duration}.'
        count_updated_objects = (len(self.records_to_update)
                                 + len(self.records_to_create))
        if count_updated_objects > 0:
            message += f'Updated: {count_updated_objects}'
            self.logger.error(message)
        else:
            message += f'Has not been updated: {count_updated_objects}'
            self.logger.error(message)

    def calculates_price_and_intra_crypto_exchange(
            self, fiat: str, asset: str, transaction_fee: float
    ) -> tuple:
        fiat_price = 1 - transaction_fee / 100
        if self.trade_type == 'BUY':
            intra_crypto_exchange = IntraCryptoExchanges.objects.get(
                from_asset=fiat, to_asset=asset)
            crypto_price = intra_crypto_exchange.price
        else:  # SELL
            intra_crypto_exchange = IntraCryptoExchanges.objects.get(
                from_asset=asset, to_asset=fiat)
            crypto_price = intra_crypto_exchange.price
        price = fiat_price * crypto_price
        return price, intra_crypto_exchange

    def generate_all_datas(self, fiat: str, asset: str,
                           transaction_method: str,
                           transaction_fee: float) -> dict:
        return {
            'asset': asset,
            'fiat': fiat,
            'trade_type': self.trade_type,
            'transaction_method': transaction_method,
            'transaction_fee': transaction_fee
        }

    def check_p2p_exchange_is_better(
            self, value_dict: dict, price: float, bank: Banks
    ) -> bool:
        p2p_exchange = self.model.objects.filter(
            crypto_exchange=self.crypto_exchange, bank=bank,
            asset=value_dict['asset'], trade_type=value_dict['trade_type'],
            fiat=value_dict['fiat'], payment_channel='P2P',
            price__isnull=False, update__updated__gte=self.update_time
        )
        if p2p_exchange.exists():
            p2p_price = p2p_exchange.get().price
            if (
                    value_dict['trade_type'] == 'BUY' and price > p2p_price
                    or value_dict['trade_type'] == 'SELL'
                    and price < p2p_price
            ):
                return True
        return False

    def get_all_datas(self) -> None:
        fiats = (self.deposit_fiats if self.trade_type == 'BUY'
                 else self.withdraw_fiats)
        for fiat, methods in fiats.items():
            for method, asset in product(methods, self.assets):
                if ((fiat, asset) in self.invalid_params_list or (asset, fiat)
                        in self.invalid_params_list):
                    continue
                transaction_method, transaction_fee = method
                value_dict = self.generate_all_datas(
                    fiat, asset, transaction_method, transaction_fee
                )
                price, intra_crypto_exchange = (
                    self.calculates_price_and_intra_crypto_exchange(
                        fiat, asset, transaction_fee
                    )
                )
                self.add_to_bulk_update_or_create(
                    value_dict, price, intra_crypto_exchange
                )

    def add_to_bulk_update_or_create(
            self, value_dict: dict, price: float,
            intra_crypto_exchange: IntraCryptoExchanges
    ) -> None:
        bank_names = []
        for name, value in self.banks_config.items():
            if self.payment_channel in value['payment_channels']:
                bank_names.append(name)
        for bank_name in bank_names:
            bank = Banks.objects.get(name=bank_name)
            target_object = self.model.objects.filter(
                crypto_exchange=self.crypto_exchange, bank=bank,
                asset=value_dict['asset'], trade_type=value_dict['trade_type'],
                fiat=value_dict['fiat'],
                transaction_method=value_dict['transaction_method'],
                intra_crypto_exchange=intra_crypto_exchange,
                payment_channel=self.payment_channel
            )
            if self.check_p2p_exchange_is_better(value_dict, price, bank):
                if target_object.exists():
                    target_object.delete()
                return
            if target_object.exists():
                updated_object = target_object.get()
                updated_object.price = price
                updated_object.transaction_fee = value_dict['transaction_fee']
                updated_object.update = self.new_update
                self.records_to_update.append(updated_object)
            else:
                created_object = self.model(
                    crypto_exchange=self.crypto_exchange, bank=bank,
                    asset=value_dict['asset'], fiat=value_dict['fiat'],
                    trade_type=value_dict['trade_type'],
                    transaction_method=value_dict['transaction_method'],
                    transaction_fee=value_dict['transaction_fee'],
                    price=price, intra_crypto_exchange=intra_crypto_exchange,
                    payment_channel=self.payment_channel,
                    update=self.new_update
                )
                self.records_to_create.append(created_object)

    def main(self):
        self.logger_start()
        self.get_all_datas()
        P2PCryptoExchangesRates.objects.bulk_create(self.records_to_create)
        P2PCryptoExchangesRates.objects.bulk_update(
            self.records_to_update, ['price', 'update', 'transaction_fee']
        )
        time_now = datetime.now(timezone.utc)
        self.duration = time_now - self.start_time
        self.new_update.duration = self.duration
        self.new_update.save()
        self.logger_end()
