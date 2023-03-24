import logging
from abc import ABC
from datetime import datetime, timedelta, timezone
from functools import reduce
from itertools import product
from typing import Any, List, Tuple

from django.db.models import Q

from arbitration.settings import (ALLOWED_PERCENTAGE, BASE_ASSET,
                                  DATA_OBSOLETE_IN_MINUTES,
                                  INTER_EXCHANGES_BEGIN_OBSOLETE_MINUTES,
                                  MINIMUM_PERCENTAGE)
from banks.models import Banks, BanksExchangeRates
from crypto_exchanges.models import (CryptoExchanges, CryptoExchangesRates,
                                     CryptoExchangesRatesUpdates,
                                     InterExchanges, InterExchangesUpdates,
                                     IntraCryptoExchangesRates)
from parsers.loggers import CalculatingLogger


class BaseCalculating(ABC):
    """
    It is an abstract base class from which other calculation classes will be
    inherited.

    Attributes:
        data_obsolete_in_minutes (int): The time in minutes since the last
            update, after which the data is considered out of date and does not
            participate in calculations.
    """
    data_obsolete_in_minutes: int = DATA_OBSOLETE_IN_MINUTES

    def __init__(self):
        from banks.banks_config import BANKS_CONFIG, INTERNATIONAL_BANKS
        self.start_time = datetime.now(timezone.utc)
        self.records_to_create = []
        self.records_to_update = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self.banks_config = BANKS_CONFIG
        self.international_banks = INTERNATIONAL_BANKS
        self.update_time = datetime.now(timezone.utc) - timedelta(
            minutes=self.data_obsolete_in_minutes
        )


class InterExchangesCalculating(BaseCalculating, CalculatingLogger, ABC):
    """
    This class is key in the project. It iterates through all possible
    transactions with the class settings. Transactions between banks, currency
    exchanges, and crypto exchanges are taken into account, including all
    available fiat currencies and cryptocurrencies, as well as various payment
    methods for deposit and withdrawal to crypto exchanges. Then it calculates
    the margin percentage and adds the best transaction chains to the database.

    Attributes:
        model: A Django model representing the exchange rates to be parsed.
        model_update: A Django model representing the updates to be made to
            the exchange rates.
        simpl (bool): Determines whether the calculations will be simple or
            complex.
        international (bool): Specifies the list of output banks, only
            international or only local.
        exit (bool): By default, false, if true, then the operation of the
            object will be prematurely terminated.
        no_crypto_exchange_bug_handler (bool): If True, there will be no check
            in __crypto_exchange_bug_handler.
        updated_fields (list): A list of fields to be updated in the model
            when new exchange rates are fetched.
        base_asset (str): Preferred cryptocurrency for internal exchanges on a
            crypto exchanges.
        output_bank (Banks): A Django model of all banks.
        output_transaction_methods (tuple): Transaction methods supported by
            output banks.
        input_crypto_exchanges: A Django model of fiat inputs to crypto
            exchanges.
        output_crypto_exchanges: A Django model of fiat output to crypto
            exchanges.
        allowed_percentage (int): The maximum margin percentage above which
            data is considered invalid. Due to an error in the crypto exchange
            data.
    """
    model = InterExchanges
    model_update = InterExchangesUpdates
    simpl: bool
    international: bool
    exit: bool = False
    no_crypto_exchange_bug_handler: bool = False
    updated_fields: List[str] = [
        'marginality_percentage', 'dynamics', 'new', 'update'
    ]
    base_asset: str = BASE_ASSET
    output_bank: Banks
    output_transaction_methods: Tuple[str]
    input_crypto_exchanges: CryptoExchangesRates
    output_crypto_exchanges: CryptoExchangesRates
    allowed_percentage: int = ALLOWED_PERCENTAGE

    def __init__(self, crypto_exchange_name: str, bank_name: str,
                 full_update: bool) -> None:
        super().__init__()
        self.crypto_exchange_name = crypto_exchange_name
        self.crypto_exchange = CryptoExchanges.objects.get(
            name=self.crypto_exchange_name
        )
        self.bank_name = bank_name
        self.bank = Banks.objects.get(name=self.bank_name)
        self.banks = self.banks_config.keys()
        self.__check_is_international()
        self.full_update = full_update
        self.__check_is_no_queue()
        self.new_update = self.model_update.objects.create(
            bank=self.bank, crypto_exchange=self.crypto_exchange,
            international=self.international, simpl=self.simpl,
            full_update=self.full_update, ended=False
        )
        self.input_bank_config = self.banks_config.get(self.bank_name)
        self.input_transaction_methods = self.input_bank_config[
            'transaction_methods']
        self.all_input_fiats = self.input_bank_config.get('currencies')
        self.created_objects = 0

    def _get_count_created_objects(self) -> None:
        """
        Sets the count of created objects to the count of records to create.
        """
        self.count_created_objects = self.created_objects

    def _get_count_updated_objects(self) -> None:
        """
        Sets the count of updated objects to the count of records to update.
        """
        self.count_updated_objects = len(self.records_to_update)

    def __check_is_no_queue(self) -> None:
        """
        Checks if the same task is running at the same time. If yes, it makes
        the exit variable equal to true so that the work of the duplicated task
        ends ahead of schedule.
        """
        pending_update = self.model_update.objects.filter(
            bank=self.bank, crypto_exchange=self.crypto_exchange,
            international=self.international, simpl=self.simpl,
            ended=False
        )
        if self.full_update:
            if pending_update.filter(full_update=self.full_update).exists():
                self.exit = True
        else:
            if pending_update.exists():
                self.exit = True

    def __check_is_international(self) -> None:
        """
        A private method that sets the banks attribute based on whether the
        transaction is international or not.
        """
        if self.international:
            self.banks = self.international_banks
        else:
            self.banks = list(self.banks)
            for international_bank in self.international_banks:
                self.banks.remove(international_bank)

    def _filter_input_crypto_exchanges(self, input_fiat: str) -> None:
        """
        A method that filters input crypto exchanges based on the given fiat.
        """
        self.input_crypto_exchanges = (
            CryptoExchangesRates.objects.select_related('update').filter(
                Q(transaction_method__in=self.input_transaction_methods) | Q(
                    transaction_method__isnull=True),
                crypto_exchange=self.crypto_exchange, bank=self.bank,
                trade_type='BUY', fiat=input_fiat, price__isnull=False,
                update__updated__gte=self.update_time
            )
        )

    def _filter_output_crypto_exchanges(self, output_fiat: str) -> None:
        """
        A method that filters output crypto exchanges based on the given fiat.
        """
        self.output_crypto_exchanges = (
            CryptoExchangesRates.objects.select_related('update').filter(
                Q(transaction_method__in=self.output_transaction_methods) | Q(
                    transaction_method__isnull=True),
                crypto_exchange=self.crypto_exchange, bank=self.output_bank,
                trade_type='SELL', fiat=output_fiat, price__isnull=False,
                update__updated__gte=self.update_time
            )
        )

    def __check_invalid_fiat_chain(
            self, input_crypto_exchange, output_crypto_exchange,
            bank_exchange=None
    ) -> bool:
        """
        This method checks if there are errors in the fiat currency transaction
        chain, if so, returns True and creates a log entry about it.
        """
        if bank_exchange is None:
            if input_crypto_exchange.fiat != output_crypto_exchange.fiat:
                self.logger.error('Invalid fiat chain without bank exchange.')
                return True
        else:
            if bank_exchange.from_fiat != output_crypto_exchange.fiat or (
                    bank_exchange.to_fiat != input_crypto_exchange.fiat
            ):
                self.logger.error('Invalid fiat chain with bank exchange.')
                return True
        return False

    def __check_invalid_asset_chain(
            self, input_crypto_exchange, interim_exchange,
            interim_second_exchange, output_crypto_exchange
    ) -> bool:
        """
        This method checks if there are errors in the crypto asset transaction
        chain, if so, returns True and creates a log entry about it.
        """
        message = (
            f'{self.__class__.__name__}, input bank: {self.bank_name}, '
            f'output bank: {output_crypto_exchange.bank.name}, crypto '
            f'exchange: {input_crypto_exchange.crypto_exchange.name}. '
        )
        if interim_exchange is None and interim_second_exchange is None:
            if input_crypto_exchange.asset != output_crypto_exchange.asset:
                message += (
                    f'Invalid asset chain without interim exchange. '
                    f'input crypto exchange asset: '
                    f'{input_crypto_exchange.asset}, output crypto exchange '
                    f'asset: {output_crypto_exchange.asset}'
                )
                self.logger.error(message)
                return True
        elif interim_second_exchange is None:
            message += 'Invalid asset chain with one interim exchange. '
            if input_crypto_exchange.asset != interim_exchange.from_asset:
                message += (
                    f'input_crypto_exchange.asset: '
                    f'{input_crypto_exchange.asset}, interim_exchange.'
                    f'from_asset: {interim_exchange.from_asset}'
                )
                self.logger.error(message)
                return True
            if output_crypto_exchange.asset != interim_exchange.to_asset:
                message += (
                    f'output_crypto_exchange.asset: '
                    f'{output_crypto_exchange.asset}, interim_exchange.'
                    f'to_asset: {interim_exchange.to_asset}'
                )
                self.logger.error(message)
                return True
        else:
            message += 'Invalid asset chain with two interim exchanges. '
            if input_crypto_exchange.asset != interim_exchange.from_asset:
                message += (
                    f'input_crypto_exchange.asset: '
                    f'{input_crypto_exchange.asset}, interim_exchange.'
                    f'from_asset: {interim_exchange.from_asset}'
                )
                self.logger.error(message)
                return True
            if interim_exchange.to_asset != interim_second_exchange.from_asset:
                message += (
                    f'interim_exchange.to_asset: {interim_exchange.to_asset}, '
                    f'interim_second_exchange.from_asset: '
                    f'{interim_second_exchange.from_asset}'
                )
                self.logger.error(message)
                return True
            if output_crypto_exchange.asset != (
                    interim_second_exchange.to_asset):
                message += (
                    f'output_crypto_exchange.asset: '
                    f'{output_crypto_exchange.asset}, interim_second_exchange.'
                    f'to_asset: {interim_second_exchange.to_asset}'
                )
                self.logger.error(message)
                return True
        return False

    def __crypto_exchange_bug_handler(
            self, marginality_percentage, input_crypto_exchange,
            interim_exchange, interim_second_exchange,
            output_crypto_exchange, bank_exchange=None
    ) -> bool:
        """
        A private method that handles crypto exchange errors if the margin
        percentage is greater than allowed_percentage.
        """
        if self.no_crypto_exchange_bug_handler:
            return False
        if marginality_percentage > self.allowed_percentage:
            diagram = self._create_diagram(
                input_crypto_exchange, interim_exchange,
                interim_second_exchange, self.output_bank,
                output_crypto_exchange, bank_exchange
            )
            message = (
                f'Not allowed percentage due to a bug on the side of the '
                f'crypto exchange. {marginality_percentage}%, {diagram} input '
                f'- {input_crypto_exchange.payment_channel}, output - '
                f'{output_crypto_exchange.payment_channel}.'
            )
            self.logger.warning(message)
            return True
        return False

    def _get_two_interim_exchanges(
            self, input_crypto_exchange: CryptoExchangesRates,
            output_crypto_exchange: CryptoExchangesRates
    ) -> tuple[Any, Any]:
        """
        A method that gets two or one interim exchanges based on input and
        output crypto exchanges.
        """
        target_interim_exchange = (
            IntraCryptoExchangesRates.objects.select_related(
                'update').filter(
                crypto_exchange=self.crypto_exchange,
                from_asset=input_crypto_exchange.asset,
                to_asset=output_crypto_exchange.asset,
                update__updated__gte=self.update_time
            )
        )
        if target_interim_exchange.exists():
            return target_interim_exchange.get(), None
        target_interim_exchange = (
            IntraCryptoExchangesRates.objects.select_related(
                'update').filter(
                crypto_exchange=self.crypto_exchange,
                from_asset=input_crypto_exchange.asset,
                to_asset=self.base_asset,
                update__updated__gte=self.update_time
            )
        )
        target_second_interim_exchange = (
            IntraCryptoExchangesRates.objects.select_related('update').filter(
                crypto_exchange=self.crypto_exchange,
                from_asset=self.base_asset,
                to_asset=output_crypto_exchange.asset,
                update__updated__gte=self.update_time
            )
        )
        if target_interim_exchange.exists(
        ) and target_second_interim_exchange.exists():
            return (target_interim_exchange.get(),
                    target_second_interim_exchange.get())
        return None, None

    def _update_complex_inter_exchanges(self) -> None:
        """
        This method is responsible for updating inter-exchange rates for a
        given bank and crypto-exchange, with an exchange within the bank. It
        filters inbound and outbound crypto exchanges based on certain
        criteria, updates bank exchange rates for inbound and outbound fiat,
        and then calculates the margin percentage for each exchange.
        """
        complex_exchanges = self.model.objects.prefetch_related(
            'input_bank', 'output_bank', 'bank_exchange',
            'input_crypto_exchange', 'output_crypto_exchange',
            'interim_crypto_exchange', 'second_interim_crypto_exchange',
            'update'
        ).filter(
            Q(input_crypto_exchange__transaction_method__in=(
                self.input_transaction_methods)) | Q(
                input_crypto_exchange__transaction_method__isnull=True),
            Q(output_crypto_exchange__transaction_method__in=(
                self.output_transaction_methods)) | Q(
                output_crypto_exchange__transaction_method__isnull=True),
            bank_exchange__isnull=False,
            input_crypto_exchange__price__isnull=False,
            output_crypto_exchange__price__isnull=False,
            input_crypto_exchange__update__updated__gte=self.update_time,
            output_crypto_exchange__update__updated__gte=self.update_time,
            bank_exchange__update__updated__gte=self.update_time,
            input_bank=self.bank, output_bank__name__in=self.banks,
            crypto_exchange=self.crypto_exchange,
            marginality_percentage__gte=(MINIMUM_PERCENTAGE - 1),
        )
        if complex_exchanges.count() == 0:
            self.full_update = True
            self.main()
            return
        for complex_exchange in complex_exchanges:
            input_crypto_exchange = complex_exchange.input_crypto_exchange
            interim_exchange = complex_exchange.interim_crypto_exchange
            interim_second_exchange = (
                complex_exchange.second_interim_crypto_exchange)
            output_crypto_exchange = complex_exchange.output_crypto_exchange
            bank_exchange = complex_exchange.bank_exchange
            marginality_percentage = (
                self._calculate_marginality_percentage(
                    input_crypto_exchange, interim_exchange,
                    interim_second_exchange, output_crypto_exchange,
                    bank_exchange
                )
            )
            if marginality_percentage < MINIMUM_PERCENTAGE:
                continue
            if self.__crypto_exchange_bug_handler(
                    marginality_percentage, input_crypto_exchange,
                    interim_exchange, interim_second_exchange,
                    output_crypto_exchange, bank_exchange
            ):
                continue
            self._add_to_bulk_update_or_create_and_bulk_create(
                input_crypto_exchange, interim_exchange,
                interim_second_exchange, output_crypto_exchange,
                marginality_percentage, bank_exchange, complex_exchange
            )

    def _get_complex_inter_exchanges(self) -> None:
        """
        This method performs fungible exchange calculations for different
        banks, iterating over banks and currencies to find profitable fungible
        exchanges between inbound and outbound crypto exchanges. With an
        exchange inside the bank. It filters out any unprofitable
        cryptocurrency exchanges and generates profits into a bulk list to
        upgrade or create.
        """
        for output_bank_name in self.banks:
            self.output_bank = Banks.objects.get(name=output_bank_name)
            output_bank_config = self.banks_config.get(output_bank_name)
            self.output_transaction_methods = output_bank_config[
                'transaction_methods']
            if not self.full_update:
                self._update_complex_inter_exchanges()
                continue
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
                self._filter_input_crypto_exchanges(input_fiat)
                self._filter_output_crypto_exchanges(output_fiat)
                for input_crypto_exchange, output_crypto_exchange in product(
                        self.input_crypto_exchanges,
                        self.output_crypto_exchanges
                ):
                    input_asset = input_crypto_exchange.asset
                    output_asset = output_crypto_exchange.asset
                    if input_asset != output_asset:
                        interim_exchange, interim_second_exchange = (
                            self._get_two_interim_exchanges(
                                input_crypto_exchange, output_crypto_exchange
                            )
                        )
                    else:
                        interim_exchange = None
                        interim_second_exchange = None
                    for bank_exchange in bank_exchanges:
                        marginality_percentage = (
                            self._calculate_marginality_percentage(
                                input_crypto_exchange, interim_exchange,
                                interim_second_exchange,
                                output_crypto_exchange, bank_exchange
                            )
                        )
                        if self.__check_invalid_fiat_chain(
                                input_crypto_exchange, output_crypto_exchange,
                                bank_exchange
                        ):
                            continue
                        if self.__check_invalid_asset_chain(
                                input_crypto_exchange, interim_exchange,
                                interim_second_exchange, output_crypto_exchange
                        ):
                            continue
                        if marginality_percentage < MINIMUM_PERCENTAGE:
                            continue
                        if self.__crypto_exchange_bug_handler(
                                marginality_percentage,
                                input_crypto_exchange, interim_exchange,
                                interim_second_exchange,
                                output_crypto_exchange, bank_exchange
                        ):
                            continue
                        self._add_to_bulk_update_or_create_and_bulk_create(
                            input_crypto_exchange, interim_exchange,
                            interim_second_exchange, output_crypto_exchange,
                            marginality_percentage, bank_exchange
                        )

    def _update_simpl_inter_exchanges(self) -> None:
        """
        This method is responsible for updating inter-exchange rates for a
        given bank and crypto-exchange, without an exchange within the bank.
        It filters inbound and outbound crypto exchanges based on certain
        criteria, updates bank exchange rates for inbound and outbound fiat,
        and then calculates the margin percentage for each exchange.
        """
        complex_exchanges = self.model.objects.prefetch_related(
            'input_bank', 'output_bank', 'input_crypto_exchange',
            'output_crypto_exchange', 'interim_crypto_exchange',
            'second_interim_crypto_exchange', 'update'
        ).filter(
            Q(input_crypto_exchange__transaction_method__in=(
                self.input_transaction_methods)) | Q(
                input_crypto_exchange__transaction_method__isnull=True),
            Q(output_crypto_exchange__transaction_method__in=(
                self.output_transaction_methods)) | Q(
                output_crypto_exchange__transaction_method__isnull=True),
            bank_exchange__isnull=True,
            input_crypto_exchange__price__isnull=False,
            output_crypto_exchange__price__isnull=False,
            input_crypto_exchange__update__updated__gte=self.update_time,
            output_crypto_exchange__update__updated__gte=self.update_time,
            input_bank=self.bank, output_bank__name__in=self.banks,
            crypto_exchange=self.crypto_exchange,
            marginality_percentage__gte=(MINIMUM_PERCENTAGE - 1),
        )
        if complex_exchanges.count() == 0:
            self.full_update = True
            self.main()
            return
        for complex_exchange in complex_exchanges:
            input_crypto_exchange = complex_exchange.input_crypto_exchange
            interim_exchange = complex_exchange.interim_crypto_exchange
            interim_second_exchange = (
                complex_exchange.second_interim_crypto_exchange)
            output_crypto_exchange = complex_exchange.output_crypto_exchange
            marginality_percentage = (
                self._calculate_marginality_percentage(
                    input_crypto_exchange, interim_exchange,
                    interim_second_exchange, output_crypto_exchange,
                )
            )
            if marginality_percentage < MINIMUM_PERCENTAGE:
                continue
            if self.__crypto_exchange_bug_handler(
                    marginality_percentage, input_crypto_exchange,
                    interim_exchange, interim_second_exchange,
                    output_crypto_exchange
            ):
                continue
            self._add_to_bulk_update_or_create_and_bulk_create(
                input_crypto_exchange, interim_exchange,
                interim_second_exchange, output_crypto_exchange,
                marginality_percentage, complex_exchange=complex_exchange
            )

    def _get_simpl_inter_exchanges(self) -> None:
        """
        This method performs fungible exchange calculations for different
        banks, iterating over banks and currencies to find profitable fungible
        exchanges between inbound and outbound crypto exchanges. No exchange
        within the bank. It filters out any unprofitable cryptocurrency
        exchanges and generates profits into a bulk list to upgrade or create.
        """
        for output_bank_name in self.banks:
            self.output_bank = Banks.objects.get(name=output_bank_name)
            output_bank_config = self.banks_config.get(output_bank_name)
            self.output_transaction_methods = output_bank_config[
                'transaction_methods']
            if not self.full_update:
                self._update_simpl_inter_exchanges()
                continue
            all_output_fiats = output_bank_config.get('currencies')
            for fiat in self.all_input_fiats:
                if fiat not in all_output_fiats:
                    continue
                self._filter_input_crypto_exchanges(fiat)
                self._filter_output_crypto_exchanges(fiat)
                for input_crypto_exchange, output_crypto_exchange in product(
                        self.input_crypto_exchanges,
                        self.output_crypto_exchanges
                ):
                    input_asset = input_crypto_exchange.asset
                    output_asset = output_crypto_exchange.asset
                    if input_asset != output_asset:
                        interim_exchange, interim_second_exchange = (
                            self._get_two_interim_exchanges(
                                input_crypto_exchange, output_crypto_exchange
                            )
                        )
                        if interim_exchange is None:
                            continue
                    else:
                        interim_exchange = None
                        interim_second_exchange = None
                    marginality_percentage = (
                        self._calculate_marginality_percentage(
                            input_crypto_exchange, interim_exchange,
                            interim_second_exchange, output_crypto_exchange
                        )
                    )
                    if self.__check_invalid_fiat_chain(
                            input_crypto_exchange, output_crypto_exchange
                    ):
                        continue
                    if self.__check_invalid_asset_chain(
                            input_crypto_exchange, interim_exchange,
                            interim_second_exchange, output_crypto_exchange
                    ):
                        continue
                    if marginality_percentage < MINIMUM_PERCENTAGE:
                        continue
                    if self.__crypto_exchange_bug_handler(
                            marginality_percentage, input_crypto_exchange,
                            interim_exchange, interim_second_exchange,
                            output_crypto_exchange
                    ):
                        continue
                    self._add_to_bulk_update_or_create_and_bulk_create(
                        input_crypto_exchange, interim_exchange,
                        interim_second_exchange, output_crypto_exchange,
                        marginality_percentage
                    )

    def __marginality_percentage_handler(self, *args: Any) -> None:
        """
        This method tries to catch a fucking error, which dick understand where
        it comes from once 1000+ iterations.
        """
        for arg in args:
            if arg is None:
                message = f'Intangible fucking error: {arg} is NoneType.'
                self.logger.error(message)

    def _calculate_marginality_percentage(
            self, input_crypto_exchange, interim_exchange,
            interim_second_exchange, output_crypto_exchange,
            bank_exchange=None
    ) -> float:
        """
        This method calculates the marginality percentage for a given set of
        input, interim, and output crypto exchanges, as well as bank exchanges,
        if provided.
        """
        interim_exchange_price = (1 if interim_exchange is None
                                  else interim_exchange.price)
        second_interim_exchange_price = (1 if interim_second_exchange is None
                                         else interim_second_exchange.price)
        bank_exchange_price = (1 if bank_exchange is None
                               else bank_exchange.price)
        self.__marginality_percentage_handler(
            input_crypto_exchange.price, interim_exchange_price,
            second_interim_exchange_price, output_crypto_exchange.price,
            bank_exchange_price
        )
        marginality_percentage = (
            reduce(lambda x, y: x * y, (
                input_crypto_exchange.price, interim_exchange_price,
                second_interim_exchange_price, output_crypto_exchange.price,
                bank_exchange_price
            )) - 1
        ) * 100
        return round(marginality_percentage, 2)

    def _create_diagram(
            self, input_crypto_exchange, interim_exchange,
            interim_second_exchange, output_bank, output_crypto_exchange,
            bank_exchange=None
    ) -> str:
        """
        This method creates a diagram of the exchange process, showing the
        different exchanges that occur in the process.
        """
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
        if_one_bank = self.bank != output_bank
        if bank_exchange and output_bank == bank_exchange.bank and if_one_bank:
            if bank_exchange.currency_market:
                diagram += f' ⇨ {bank_exchange.currency_market.name} '
            else:
                diagram += f' ⇨ {output_bank.name} '
            diagram += f'{bank_exchange.to_fiat}'
        return diagram

    def _add_to_bulk_update_or_create_and_bulk_create(
            self, input_crypto_exchange, interim_exchange,
            interim_second_exchange, output_crypto_exchange,
            marginality_percentage, bank_exchange=None, complex_exchange=None
    ) -> None:
        """
        This method adds a set of profitable crypto exchanges to a bulk list
        for update or creation.
        """
        if self.full_update:
            target_object = self.model.objects.filter(
                crypto_exchange=self.crypto_exchange, input_bank=self.bank,
                output_bank=self.output_bank,
                input_crypto_exchange=input_crypto_exchange,
                interim_crypto_exchange=interim_exchange,
                second_interim_crypto_exchange=interim_second_exchange,
                output_crypto_exchange=output_crypto_exchange,
                bank_exchange=bank_exchange
            )
            if not target_object.exists():
                self.model.objects.create(
                    crypto_exchange=self.crypto_exchange, input_bank=self.bank,
                    output_bank=self.output_bank,
                    input_crypto_exchange=input_crypto_exchange,
                    interim_crypto_exchange=interim_exchange,
                    second_interim_crypto_exchange=interim_second_exchange,
                    output_crypto_exchange=output_crypto_exchange,
                    bank_exchange=bank_exchange,
                    marginality_percentage=marginality_percentage,
                    diagram=self._create_diagram(
                        input_crypto_exchange, interim_exchange,
                        interim_second_exchange, self.output_bank,
                        output_crypto_exchange, bank_exchange
                    ), dynamics=None, new=True, update=self.new_update
                )
                self.created_objects += 1
                return
            inter_exchange = target_object.get()
        else:
            inter_exchange = complex_exchange
        if inter_exchange.marginality_percentage > marginality_percentage:
            inter_exchange.dynamics = 'fall'
        elif (
            inter_exchange.marginality_percentage < marginality_percentage
        ):
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

    def main(self) -> None:
        """
        This method is the main method of the class and is responsible for
        running the entire process. It calls the _get_complex_inter_exchanges
        method or _get_complex_inter_exchanges method to generate the data,
        then bulk creates or updates the records in the model. After that, it
        calculates the duration of the process and saves it to the database. If
        an error occurs during the process, it logs the error and raises an
        exception.
        """
        try:
            if self.exit:
                self.new_update.delete()
                self._logger_queue_overflowing()
                return
            self._logger_start()
            if self.simpl:
                self._get_simpl_inter_exchanges()
            else:
                self._get_complex_inter_exchanges()
            self.model.objects.bulk_update(
                self.records_to_update, self.updated_fields
            )
            time_now = datetime.now(timezone.utc)
            self.duration = time_now - self.start_time
            self.new_update.updated = time_now
            self.new_update.duration = self.duration
            self.new_update.ended = True
            self.new_update.save()
            self._logger_end()
        except Exception as error:
            self.new_update.ended = True
            self.new_update.save()
            self._logger_error(error)
            raise Exception


class Card2Wallet2CryptoExchangesCalculating(BaseCalculating,
                                             CalculatingLogger, ABC):
    model = CryptoExchangesRates
    model_update = CryptoExchangesRatesUpdates
    crypto_exchange_name: str
    payment_channel = 'Card2Wallet2CryptoExchange'
    updated_fields: List[str] = ['price', 'update', 'transaction_fee']
    data_obsolete_in_minutes: int = DATA_OBSOLETE_IN_MINUTES

    def __init__(self, trade_type: str) -> None:
        super().__init__()
        from crypto_exchanges.crypto_exchanges_config import (
            CRYPTO_EXCHANGES_CONFIG)
        self.crypto_exchange = CryptoExchanges.objects.get(
            name=self.crypto_exchange_name
        )
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

    def _get_count_created_objects(self) -> None:
        """
        Sets the count of created objects to the count of records to create.
        """
        self.count_created_objects = len(self.records_to_create)

    def _get_count_updated_objects(self) -> None:
        """
        Sets the count of updated objects to the count of records to update.
        """
        self.count_updated_objects = len(self.records_to_update)

    def _calculates_price_and_intra_crypto_exchange(
            self, fiat: str, asset: str, transaction_fee: float
    ) -> tuple or None:
        """
        Calculates the price and intra-crypto exchange rates for the given
        fiat, asset, and transaction fee. Returns a tuple with the price and
        intra-crypto exchange rate or None if the rates could not be
        calculated.
        """
        fiat_price = 1 - transaction_fee / 100
        if self.trade_type == 'BUY':
            target_intra_crypto_exchange = (
                IntraCryptoExchangesRates.objects.select_related(
                    'update').filter(
                    crypto_exchange=self.crypto_exchange,
                    from_asset=fiat, to_asset=asset,
                    update__updated__gte=self.update_time
                )
            )
        else:  # SELL
            target_intra_crypto_exchange = (
                IntraCryptoExchangesRates.objects.select_related(
                    'update').filter(
                    crypto_exchange=self.crypto_exchange,
                    from_asset=asset, to_asset=fiat,
                    update__updated__gte=self.update_time
                )
            )
        if target_intra_crypto_exchange.exists():
            intra_crypto_exchange = target_intra_crypto_exchange.get()
            crypto_price = intra_crypto_exchange.price
            price = fiat_price * crypto_price
            return price, intra_crypto_exchange

    def _generate_all_datas(self, fiat: str, asset: str,
                            transaction_method: str,
                            transaction_fee: float) -> dict:
        """
        Generates a dictionary with data for a crypto exchange transaction.
        """
        return {
            'asset': asset,
            'fiat': fiat,
            'trade_type': self.trade_type,
            'transaction_method': transaction_method,
            'transaction_fee': transaction_fee
        }

    def __check_p2p_exchange_is_better(self, value_dict: dict, price: float,
                                       bank: Banks) -> bool:
        """
        Checks if a P2P exchange offers a better price than the current
        exchange.
        """
        p2p_exchange = self.model.objects.select_related('update').filter(
            crypto_exchange=self.crypto_exchange, bank=bank,
            asset=value_dict['asset'], trade_type=value_dict['trade_type'],
            fiat=value_dict['fiat'], payment_channel='P2P',
            price__isnull=False, update__updated__gte=self.update_time
        )
        if p2p_exchange.exists():
            p2p_price = p2p_exchange.get().price
            if_bad_buy_price = (
                value_dict['trade_type'] == 'BUY' and price > p2p_price)
            if_bad_sell_price = (
                value_dict['trade_type'] == 'SELL' and price < p2p_price)
            if if_bad_buy_price or if_bad_sell_price:
                return True
        return False

    def _add_to_bulk_update_or_create(
            self, value_dict: dict, price: float,
            intra_crypto_exchange: IntraCryptoExchangesRates
    ) -> None:
        """
        Adds a new record to the records_to_create or records_to_update list
        depending on whether a record with the given data already exists.
        """
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
            if self.__check_p2p_exchange_is_better(value_dict, price, bank):
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

    def _get_all_datas(self) -> None:
        """
        This method iterates over the deposit or withdrawal fiats and the
        available assets and generates all the necessary data for each
        combination. It skips the invalid combinations of fiat and asset, and
        then calls other methods to generate the price and intra-crypto
        exchange values. Finally, it adds the data to a bulk update or create
        list.
        """
        fiats = (self.deposit_fiats if self.trade_type == 'BUY'
                 else self.withdraw_fiats)
        for fiat, methods in fiats.items():
            for method, asset in product(methods, self.assets):
                if ((fiat, asset) in self.invalid_params_list or (asset, fiat)
                        in self.invalid_params_list):
                    continue
                transaction_method, transaction_fee = method
                value_dict = self._generate_all_datas(
                    fiat, asset, transaction_method, transaction_fee
                )
                price_and_exchange = (
                    self._calculates_price_and_intra_crypto_exchange(
                        fiat, asset, transaction_fee
                    )
                )
                if price_and_exchange is None:
                    continue
                price, intra_crypto_exchange = price_and_exchange
                self._add_to_bulk_update_or_create(
                    value_dict, price, intra_crypto_exchange
                )

    def main(self):
        """
        This method is the main method of the class and is responsible for
        running the entire process. It calls the _get_all_datas method to
        generate the data, then bulk creates or updates the records in the
        model. After that, it calculates the duration of the process and saves
        it to the database. If an error occurs during the process, it logs the
        error and raises an exception.
        """
        try:
            self._logger_start()
            self._get_all_datas()
            self.model.objects.bulk_create(self.records_to_create)
            self.model.objects.bulk_update(
                self.records_to_update, self.updated_fields
            )
            time_now = datetime.now(timezone.utc)
            self.duration = time_now - self.start_time
            self.new_update.duration = self.duration
            self.new_update.save()
            self._logger_end()
        except Exception as error:
            self._logger_error(error)
            raise Exception


class SimplInterExchangesCalculating(InterExchangesCalculating):
    """
    Child class of the InterExchangesCalculating class. To generate and
    calculate all arbitrated chains of transactions in which there is no
    intra-bank exchange and Russian banks stand at the end of the exchange.
    """
    simpl: bool = True
    international: bool = False


class SimplInternationalInterExchangesCalculating(InterExchangesCalculating):
    """
    Child class of the InterExchangesCalculating class. To generate and
    calculate all arbitrated chains of transactions in which there is no
    intra-bank exchange and non-Russian banks stand at the end of the exchange.
    """
    simpl: bool = True
    international: bool = True


class ComplexInterExchangesCalculating(InterExchangesCalculating):
    """
    Child class of the InterExchangesCalculating class. To generate and
    calculate all arbitrated chains of transactions in which there is an
    intra-bank exchange and Russian banks are at the end of the exchange.
    """
    simpl: bool = False
    international: bool = False


class ComplexInternationalInterExchangesCalculating(InterExchangesCalculating):
    """
    Child class of the InterExchangesCalculating class. To generate and
    calculate all arbitrated chains of transactions in which there is an
    intra-bank exchange and non-Russian banks are at the end of the exchange.
    """
    simpl: bool = False
    international: bool = True
