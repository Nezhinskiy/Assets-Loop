from itertools import permutations


class InsideBanks(object):
    fiats: tuple = None
    Exchanges = None
    Updates = None

    def converts_choices_to_tuple(self) -> list:
        """repackaging choices of fiats into a list of fiats."""
        return list(choice[0] for choice in self.fiats)

    def main_loop(self):
        transfer_combinations = []
        currencies: list = self.converts_choices_to_tuple()
        for initial_end_currency in currencies:  # валюта по одной
            combinable_currencies = currencies.remove(initial_end_currency)
            # for num in range(len(combinable_currencies)):  # длины последовательностей между старт финиш
            #     body_combinations: list = permutations(combinable_currencies,
            #                                            num + 1)
            #     transfer_combination1 = body_combinations.insert(
            #         initial_end_currency)
            #     transfer_combination = transfer_combination1.append(initial_end_currency)
            #     transfer_combinations.append(transfer_combination)
            print(currencies) # transfer_combinations





