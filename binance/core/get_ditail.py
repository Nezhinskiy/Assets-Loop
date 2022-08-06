from banks.banks_config import BANKS_CONFIG
from crypto_exchanges.crypto_exchanges_config import CRYPTO_EXCHANGES_CONFIG


class GetDitail:
    @staticmethod
    def get_bank_ditail() -> None:
        for bank_config in BANKS_CONFIG.values():
            bank_parser = bank_config.get('bank_parser')
            bank_parser.main()
            intra_exchange = bank_config.get('intra_exchange')
            intra_exchange.main()

    @staticmethod
    def get_crypto_exchange_ditail() -> None:
        for crypto_exchange_config in CRYPTO_EXCHANGES_CONFIG.values():
            p2p_parser = crypto_exchange_config.get('p2p_parser')
            p2p_parser.main()
            crypto_exchanges_parser = crypto_exchange_config.get(
                'crypto_exchanges_parser')
            crypto_exchanges_parser.main()