from banks.banks_registration.tinkoff import IntraTinkoff, TinkoffParser
from banks.banks_registration.wise import IntraWise, WiseParser
from crypto_exchanges.crypto_exchanges_registration.binance import (
    BinanceCryptoParser, BinanceP2PParser)


class BankP2PBank(object):
    bank_parser = (TinkoffParser, WiseParser)
    intra_exchange = (IntraTinkoff, IntraWise)
    p2p_parser = (BinanceP2PParser,)
    crypto_exchanges_parsers = (BinanceCryptoParser,)


    fiats: tuple = None
    Exchanges = None
    InsideExchanges = None
    Updates = None
    currencies_with_requisites = None
    percentage_round_to = 2
    BANKING_CONFIG = None

    # def start(self):
    #     for name_of_bank, config_of_bank in self.BANKING_CONFIG:
    #         InsideBankExchanges = config_of_bank['inside_bank_exchanges']
    #         if InsideBankExchanges.object.filter(
    #                 marginality_percentage__gt=0
    #         ).exists():
    #             pass
    #
    # def main(self):

