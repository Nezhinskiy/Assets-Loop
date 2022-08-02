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

    def main_loop(self):
        transfer_combinations = []
        all_exchanges = self.Exchanges.objects.select_related('update').all()
        all_fiats = self.converts_choices_to_list()
        for initial_end_fiat in all_fiats:
            combinable_fiats: list = self.converts_choices_to_list()
            combinable_fiats.remove(initial_end_fiat)
            print(combinable_fiats, initial_end_fiat)
            for index in range(len(combinable_fiats)):
                body_combinations = list(permutations(combinable_fiats, index + 1))
                print(index, body_combinations)
                for body_combination in body_combinations:
                    combination = list(body_combination)
                    combination.insert(0, initial_end_fiat)
                    combination.append(initial_end_fiat)
                    marginality_percentage = self.create_marginality_percentage(
                        combination, all_exchanges
                    )
                    print(combination, marginality_percentage)



















        # currencies: list = self.converts_choices_to_tuple()
        # for initial_end_currency in currencies:  # валюта по одной
        #     combinable_currencies: list = self.converts_choices_to_tuple()
        #     # for num in range(len(combinable_currencies)):  # длины последовательностей между старт финиш
        #         # body_combinations: list = permutations(combinable_currencies,
        #         #                                        num + 1)
        #         # transfer_combination1 = body_combinations.insert(
        #         #     initial_end_currency)
        #         # transfer_combination = transfer_combination1.append(initial_end_currency)
        #         # transfer_combinations.append(transfer_combination)
        #     print(currencies, initial_end_currency) # transfer_combinations
