from datetime import datetime
import math
from itertools import permutations


class InsideBanks(object):
    fiats: tuple = None
    Exchanges = None
    InsideExchanges = None
    Updates = None
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
            self, new_update, records_to_update, records_to_create,
            combination, marginality_percentage
    ):
        target_object = self.InsideExchanges.objects.filter(
            list_of_transfers=combination
        )
        if target_object.exists():
            updated_object = self.InsideExchanges.objects.get(
                list_of_transfers=combination
            )
            if updated_object.marginality_percentage == marginality_percentage:
                return
            updated_object.marginality_percentage = marginality_percentage
            updated_object.update = new_update
            records_to_update.append(updated_object)
        else:
            created_object = self.InsideExchanges(
                list_of_transfers=combination,
                marginality_percentage=marginality_percentage,
                update=new_update
            )
            records_to_create.append(created_object)

    def create_combinations(self, new_update, all_exchanges,
                            records_to_update, records_to_create):
        all_fiats = self.converts_choices_to_list()
        for initial_end_fiat in all_fiats:
            combinable_fiats: list = self.converts_choices_to_list()
            combinable_fiats.remove(initial_end_fiat)
            for index in range(len(combinable_fiats)):
                body_combinations = list(permutations(combinable_fiats, index + 1))
                for body_combination in body_combinations:
                    combination = list(body_combination)
                    combination.insert(0, initial_end_fiat)
                    combination.append(initial_end_fiat)
                    marginality_percentage = self.create_marginality_percentage(
                        combination, all_exchanges
                    )
                    self.add_to_bulk_update_or_create(
                        new_update, records_to_update, records_to_create,
                        combination, marginality_percentage
                    )

    def main(self):
        start_time = datetime.now()
        new_update = self.Updates.objects.create()
        all_exchanges = self.Exchanges.objects.select_related('update').all()
        records_to_update = []
        records_to_create = []
        self.create_combinations(
            new_update, all_exchanges, records_to_update, records_to_create
        )
        self.InsideExchanges.objects.bulk_create(records_to_create)
        self.InsideExchanges.objects.bulk_update(
            records_to_update, ['marginality_percentage', 'update']
        )
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()
