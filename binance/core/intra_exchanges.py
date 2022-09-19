import math
import sys
from datetime import datetime
from itertools import permutations, product

from banks.models import (Banks, BanksExchangeRates, IntraBanksExchanges,
                          IntraBanksExchangesUpdates,
                          IntraBanksNotLoopedExchanges,
                          IntraBanksNotLoopedExchangesUpdates)
from crypto_exchanges.models import (BestCombinationPaymentChannels,
                                     BestCombinationPaymentChannelsUpdates,
                                     BestPaymentChannels,
                                     BestPaymentChannelsUpdates,
                                     Card2CryptoExchanges,
                                     Card2Wallet2CryptoExchanges,
                                     CryptoExchanges, IntraCryptoExchanges,
                                     P2PCryptoExchangesRates)


def get_related_exchange(meta_exchange):
    model = meta_exchange.payment_channel_model
    id = meta_exchange.exchange_id
    return getattr(sys.modules[__name__], model).objects.get(id=id)


class IntraBanks(object):
    bank_name = None
    fiats: tuple = None
    currencies_with_requisites = None
    percentage_round_to = 2

    def converts_choices_to_list(self) -> list:
        """repackaging choices of fiats into a list of fiats."""
        return list(choice[0] for choice in self.fiats)

    def create_iteration_combinations(self, combination):
        last = len(combination) - 1
        iteration_combinations = []
        for index_pair_first, fiat_pair_first in enumerate(combination):
            if index_pair_first == last:
                break
            for index_pair_second, fiat_pair_second in enumerate(combination):
                if index_pair_second == index_pair_first + 1:
                    fiat_pair = (fiat_pair_first, fiat_pair_second)
                    iteration_combinations.append(fiat_pair)
        return iteration_combinations

    def create_marginality_percentage(self, combination, all_exchanges):
        iteration_combinations = self.create_iteration_combinations(combination)
        iteration_prices = []
        for fiat_pair in iteration_combinations:
            fiat_pair_exchange = all_exchanges.get(from_fiat=fiat_pair[0],
                                                   to_fiat=fiat_pair[1])
            iteration_price = fiat_pair_exchange.price
            iteration_prices.append(iteration_price)
        accurate_marginality_percentage = math.prod(
            iteration_prices) * 100 - 100
        marginality_percentage = round(accurate_marginality_percentage,
                                       self.percentage_round_to)
        return marginality_percentage

    def add_to_bulk_update_or_create(
            self, bank, new_update, records_to_update, records_to_create,
            combination, marginality_percentage
    ):
        target_object = IntraBanksExchanges.objects.filter(
            bank=bank,
            list_of_transfers=combination
        )
        if target_object.exists():
            updated_object = IntraBanksExchanges.objects.get(
                bank=bank,
                list_of_transfers=combination
            )
            if updated_object.marginality_percentage == marginality_percentage:
                return
            updated_object.marginality_percentage = marginality_percentage
            updated_object.update = new_update
            records_to_update.append(updated_object)
        else:
            created_object = IntraBanksExchanges(
                bank=bank,
                list_of_transfers=combination,
                marginality_percentage=marginality_percentage,
                update=new_update
            )
            records_to_create.append(created_object)

    def create_combinations(self, bank, new_update, all_exchanges,
                            records_to_update, records_to_create):
        from banks.banks_config import BANKS_CONFIG
        bank_config = BANKS_CONFIG.get(self.bank_name)
        all_fiats = bank_config.get('currencies')
        for initial_end_fiat in all_fiats:
            if initial_end_fiat not in self.currencies_with_requisites:
                continue
            combinable_fiats: list = list(bank_config.get('currencies'))
            combinable_fiats.remove(initial_end_fiat)
            for index in range(len(combinable_fiats)):
                if index == 2:
                    break
                body_combinations = list(permutations(combinable_fiats,
                                                      index + 1))
                for body_combination in body_combinations:
                    combination = list(body_combination)
                    combination.insert(0, initial_end_fiat)
                    combination.append(initial_end_fiat)
                    marginality_percentage = self.create_marginality_percentage(
                        combination, all_exchanges
                    )
                    self.add_to_bulk_update_or_create(
                        bank, new_update, records_to_update, records_to_create,
                        combination, marginality_percentage
                    )

    def main(self):
        start_time = datetime.now()
        bank = Banks.objects.get(name=self.bank_name)
        new_update = IntraBanksExchangesUpdates.objects.create(bank=bank)
        all_exchanges = BanksExchangeRates.objects.all()
        records_to_update = []
        records_to_create = []
        self.create_combinations(
            bank, new_update, all_exchanges, records_to_update,
            records_to_create
        )
        IntraBanksExchanges.objects.bulk_create(records_to_create)
        IntraBanksExchanges.objects.bulk_update(
            records_to_update, ['marginality_percentage', 'update']
        )
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()


class IntraBanksNotLooped(IntraBanks):
    bank_name = None

    def create_price_percentage_not_looped(self, bank, combination,
                                           all_exchanges):
        iteration_combinations = self.create_iteration_combinations(combination)
        iteration_prices = []
        for fiat_pair in iteration_combinations:
            fiat_pair_exchange = all_exchanges.get(
                from_fiat=fiat_pair[0], to_fiat=fiat_pair[1], bank=bank)
            iteration_price = fiat_pair_exchange.price
            iteration_prices.append(iteration_price)
        price = math.prod(iteration_prices)
        return price

    def create_marginality_percentage_not_looped(self, analogous_exchange,
                                                 price):
        analogous_exchange_price = analogous_exchange.price
        accurate_marginality_percentage = price / (
                analogous_exchange_price / 100) - 100
        marginality_percentage = round(accurate_marginality_percentage,
                                       self.percentage_round_to)
        return marginality_percentage

    def add_to_bulk_update_or_create_not_looped(
            self, bank, new_update, records_to_update, records_to_create,
            combination, analogous_exchange, price, marginality_percentage
    ):
        target_object = IntraBanksNotLoopedExchanges.objects.filter(
            bank=bank,
            list_of_transfers=combination
        )
        if target_object.exists():
            updated_object = IntraBanksNotLoopedExchanges.objects.get(
                bank=bank,
                list_of_transfers=combination
            )
            if (
                    updated_object.marginality_percentage
                    == marginality_percentage and updated_object.price
                    == price
            ):
                return
            updated_object.price = price
            updated_object.marginality_percentage = marginality_percentage
            updated_object.update = new_update
            records_to_update.append(updated_object)
        else:
            created_object = IntraBanksNotLoopedExchanges(
                bank=bank,
                list_of_transfers=combination,
                price=price,
                marginality_percentage=marginality_percentage,
                analogous_exchange=analogous_exchange,
                update=new_update
            )
            records_to_create.append(created_object)

    def create_combinations(self, bank, new_update, all_exchanges,
                            records_to_update, records_to_create):
        from banks.banks_config import BANKS_CONFIG
        bank_config = BANKS_CONFIG.get(self.bank_name)
        all_fiats = bank_config.get('currencies')
        input_currencies_with_requisites = bank_config.get(
            'currencies_with_requisites')
        output_currencies_with_requisites = bank_config.get(
            'currencies_with_requisites')
        for input_currency, output_currency in product(
                input_currencies_with_requisites,
                output_currencies_with_requisites):
            if input_currency == output_currency:
                continue
            combinable_fiats: list = list(all_fiats)
            combinable_fiats.remove(input_currency)
            combinable_fiats.remove(output_currency)
            for index in range(len(combinable_fiats)):
                if index == 3:
                    break
                body_combinations = list(permutations(combinable_fiats,
                                                      index + 1))
                for body_combination in body_combinations:
                    combination = list(body_combination)
                    combination.insert(0, input_currency)
                    combination.append(output_currency)
                    analogous_exchange = all_exchanges.get(
                        from_fiat=input_currency, to_fiat=output_currency,
                        bank=bank
                    )
                    price = self.create_price_percentage_not_looped(
                        bank, combination, all_exchanges
                    )
                    marginality_percentage = (
                        self.create_marginality_percentage_not_looped(
                            analogous_exchange, price
                        )
                    )
                    self.add_to_bulk_update_or_create_not_looped(
                        bank, new_update, records_to_update, records_to_create,
                        combination, analogous_exchange, price,
                        marginality_percentage
                    )

    def main(self):
        start_time = datetime.now()
        bank = Banks.objects.get(name=self.bank_name)
        new_update = IntraBanksNotLoopedExchangesUpdates.objects.create(
            bank=bank)
        all_exchanges = BanksExchangeRates.objects.all()
        records_to_update = []
        records_to_create = []
        self.create_combinations(
            bank, new_update, all_exchanges, records_to_update,
            records_to_create
        )
        IntraBanksNotLoopedExchanges.objects.bulk_create(records_to_create)
        IntraBanksNotLoopedExchanges.objects.bulk_update(
            records_to_update, ['price', 'marginality_percentage', 'update']
        )
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()


class BestCryptoExchanges(object):
    def __init__(self, crypto_exchange_name):
        self.crypto_exchange_name = crypto_exchange_name
        self.crypto_exchange = CryptoExchanges.objects.get(
            name=crypto_exchange_name
        )

    def add_to_bulk_update_or_create(
            self, bank, fiat, asset, trade_type, best_price,
            best_exchange_model, best_exchange_id, new_update,
            records_to_update, records_to_create
    ):
        target_object = BestPaymentChannels.objects.filter(
            crypto_exchange=self.crypto_exchange, bank=bank, fiat=fiat,
            asset=asset, trade_type=trade_type,
        )
        if target_object.exists():
            updated_object = target_object.get()
            if (updated_object.payment_channel_model == best_exchange_model
                    and updated_object.exchange_id == best_exchange_id):
                if updated_object.price == best_price:
                    return
                new_update = updated_object.update
            updated_object.price = best_price
            updated_object.payment_channel_model = best_exchange_model
            updated_object.exchange_id = best_exchange_id
            updated_object.update = new_update
            records_to_update.append(updated_object)
        else:
            created_object = BestPaymentChannels(
                crypto_exchange=self.crypto_exchange, bank=bank, fiat=fiat,
                asset=asset, trade_type=trade_type, price=best_price,
                payment_channel_model=best_exchange_model,
                exchange_id=best_exchange_id, update=new_update
            )
            records_to_create.append(created_object)

    def get_best_exchanges(self, new_update, records_to_update,
                           records_to_create):
        from banks.banks_config import BANKS_CONFIG
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        banks = BANKS_CONFIG.keys()
        crypto_exchanges_configs = CRYPTO_EXCHANGES_CONFIG.get(
            self.crypto_exchange_name)
        valid_payment_channels = crypto_exchanges_configs.get('payment_channels')
        assets = crypto_exchanges_configs.get('assets')
        trade_types = crypto_exchanges_configs.get('trade_types')

        for bank_name in banks:
            bank = Banks.objects.get(name=bank_name)
            bank_configs = BANKS_CONFIG[bank_name]
            bank_payment_channels = bank_configs['payment_channels']
            fiats = bank_configs['currencies']
            for fiat, asset, trade_type in product(fiats, assets, trade_types):
                exchanges_dict = {}
                for bank_payment_channel in bank_payment_channels:
                    if bank_payment_channel not in valid_payment_channels:
                        continue
                    checked_object = bank_payment_channel.objects.filter(
                        crypto_exchange=self.crypto_exchange,
                        trade_type=trade_type, fiat=fiat, asset=asset
                        )
                    if not checked_object.exists():
                        continue
                    exchange = (checked_object.get(bank=bank)
                                if hasattr(bank_payment_channel, 'bank')
                                else checked_object.get())
                    price = exchange.price
                    if price is None:
                        continue
                    exchange_info = (exchange.__class__.__name__, exchange.pk)
                    exchanges_dict[price] = exchange_info
                if not exchanges_dict:
                    continue
                best_price = max(exchanges_dict.keys())
                best_exchange_model = exchanges_dict[best_price][0]
                best_exchange_id = exchanges_dict[best_price][1]
                self.add_to_bulk_update_or_create(
                    bank, fiat, asset, trade_type, best_price,
                    best_exchange_model, best_exchange_id, new_update,
                    records_to_update, records_to_create
                )

    def main(self):
        start_time = datetime.now()
        new_update = BestPaymentChannelsUpdates.objects.create(
            crypto_exchange=self.crypto_exchange
        )
        records_to_update = []
        records_to_create = []
        self.get_best_exchanges(
            new_update, records_to_update, records_to_create
        )
        BestPaymentChannels.objects.bulk_create(records_to_create)
        BestPaymentChannels.objects.bulk_update(
            records_to_update,
            ['price', 'payment_channel_model', 'exchange_id', 'update']
        )
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()


class BestTotalCryptoExchanges(object):
    def __init__(self, crypto_exchange_name):
        self.crypto_exchange_name = crypto_exchange_name
        self.crypto_exchange = CryptoExchanges.objects.get(
            name=crypto_exchange_name
        )

    def add_to_bulk_update_or_create(
            self, new_update, records_to_update, records_to_create,
            best_total_price, best_total_exchange
    ):
        input_meta_exchange, interim_exchange, output_meta_exchange = (
            best_total_exchange)
        input_exchange = get_related_exchange(input_meta_exchange)
        input_bank = input_meta_exchange.bank
        from_fiat = input_exchange.fiat
        output_exchange = get_related_exchange(output_meta_exchange)
        output_bank = output_meta_exchange.bank
        to_fiat = output_exchange.fiat
        target_object = BestCombinationPaymentChannels.objects.filter(
            crypto_exchange=self.crypto_exchange, input_bank=input_bank,
            output_bank=output_bank, from_fiat=from_fiat, to_fiat=to_fiat,
        )
        if target_object.exists():
            updated_object = target_object.get()
            if (updated_object.input_exchange == input_meta_exchange
                    and updated_object.output_exchange == output_meta_exchange):
                if updated_object.price == best_total_price:
                    return
                new_update = updated_object.update
            updated_object.price = best_total_price
            updated_object.input_exchange = input_meta_exchange
            updated_object.interim_exchange = interim_exchange
            updated_object.output_exchange = output_meta_exchange
            updated_object.update = new_update
            records_to_update.append(updated_object)
        else:
            created_object = BestCombinationPaymentChannels(
                crypto_exchange=self.crypto_exchange, input_bank=input_bank,
                output_bank=output_bank, from_fiat=from_fiat, to_fiat=to_fiat,
                input_exchange=input_meta_exchange,
                interim_exchange=interim_exchange,
                output_exchange=output_meta_exchange, price=best_total_price,
                update=new_update
            )
            records_to_create.append(created_object)

    def get_best_total_exchanges(self, new_update,
                                 records_to_update, records_to_create):
        from banks.banks_config import BANKS_CONFIG
        banks = BANKS_CONFIG.keys()
        for input_bank_name in banks:
            input_bank = Banks.objects.get(name=input_bank_name)
            input_meta_exchanges = BestPaymentChannels.objects.filter(
                crypto_exchange=self.crypto_exchange, bank=input_bank,
                trade_type='BUY'
            )
            output_meta_exchanges = BestPaymentChannels.objects.filter(
                crypto_exchange=self.crypto_exchange, trade_type='SELL'
            )
            exchanges_list = {}
            for input_meta_exchange, output_meta_exchange in product(
                    input_meta_exchanges, output_meta_exchanges):
                input_exchange = get_related_exchange(input_meta_exchange)
                input_fiat = input_exchange.fiat
                input_asset = input_exchange.asset
                input_price = input_exchange.price
                output_exchange = get_related_exchange(output_meta_exchange)
                output_fiat = output_exchange.fiat
                output_asset = output_exchange.asset
                output_price = output_exchange.price
                exchanges_name = input_fiat + output_fiat
                if not exchanges_list.get(exchanges_name):
                    exchanges_list[exchanges_name] = {}
                if input_asset != output_asset:
                    interim_exchange = IntraCryptoExchanges.objects.get(
                        crypto_exchange=self.crypto_exchange,
                        from_asset=input_asset, to_asset=output_asset
                    )
                    interim_price = interim_exchange.price
                else:
                    interim_exchange = None
                    interim_price = 1
                total_price = input_price * interim_price * output_price
                total_exchange = (
                    input_meta_exchange, interim_exchange, output_meta_exchange
                )
                exchanges_list[exchanges_name][total_price] = total_exchange

            for name, similar_exchanges in exchanges_list.items():
                best_total_price = max(similar_exchanges.keys())
                best_total_exchange = similar_exchanges[best_total_price]
                self.add_to_bulk_update_or_create(
                    new_update, records_to_update, records_to_create,
                    best_total_price, best_total_exchange
                )

    def main(self):
        start_time = datetime.now()
        new_update = BestCombinationPaymentChannelsUpdates.objects.create(
            crypto_exchange=self.crypto_exchange
        )
        records_to_update = []
        records_to_create = []
        self.get_best_total_exchanges(
            new_update, records_to_update, records_to_create
        )
        BestCombinationPaymentChannels.objects.bulk_create(records_to_create)
        BestCombinationPaymentChannels.objects.bulk_update(
            records_to_update,
            ['price', 'input_exchange', 'interim_exchange',
             'output_exchange', 'update']
        )
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()







