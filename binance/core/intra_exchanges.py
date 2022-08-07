import math
from datetime import datetime
from itertools import permutations, product

from banks.models import (Banks, BanksExchangeRates, IntraBanksExchanges,
                          IntraBanksExchangesUpdates,
                          IntraBanksNotLoopedExchanges,
                          IntraBanksNotLoopedExchangesUpdates)


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
            combinable_fiats: list = bank_config.get('currencies')
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

    def create_marginality_percentage_not_looped(
            self, bank, input_currency, output_currency, combination,
            all_exchanges
    ):

        iteration_combinations = self.create_iteration_combinations(combination)
        iteration_prices = []
        for fiat_pair in iteration_combinations:
            fiat_pair_exchange = all_exchanges.get(
                from_fiat=fiat_pair[0], to_fiat=fiat_pair[1], bank=bank)
            iteration_price = fiat_pair_exchange.price
            iteration_prices.append(iteration_price)
        exchange_rate = math.prod(iteration_prices)
        analogous_exchange_rate = all_exchanges.get(
            from_fiat=input_currency, to_fiat=output_currency, bank=bank
        )
        analogous_exchange_rate_price = analogous_exchange_rate.price
        accurate_marginality_percentage = analogous_exchange_rate_price / (
                exchange_rate / 100) - 100
        marginality_percentage = round(accurate_marginality_percentage,
                                       self.percentage_round_to)
        return marginality_percentage


    def add_to_bulk_update_or_create_not_looped(
            self, bank, new_update, records_to_update, records_to_create,
            combination, marginality_percentage
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
            if updated_object.marginality_percentage == marginality_percentage:
                return
            updated_object.marginality_percentage = marginality_percentage
            updated_object.update = new_update
            records_to_update.append(updated_object)
        else:
            created_object = IntraBanksNotLoopedExchanges(
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
                    marginality_percentage = (
                        self.create_marginality_percentage_not_looped(
                            bank, input_currency, output_currency, combination,
                            all_exchanges)
                    )
                    self.add_to_bulk_update_or_create_not_looped(
                        bank, new_update, records_to_update, records_to_create,
                        combination, marginality_percentage
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
            records_to_update, ['marginality_percentage', 'update']
        )
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()
