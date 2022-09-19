from django.urls import include, path

from crypto_exchanges.views import (binance_best_crypto_exchanges,
                                    binance_card_2_crypto_exchanges,
                                    binance_crypto, binance_fiat_crypto_list,
                                    card_2_wallet_2_crypto, p2p_binance)

app_name = 'crypto_exchanges'

urlpatterns = [
    path('1/', p2p_binance, name="p2p_binance"),
    path('100/', binance_crypto, name="binance_crypto"),
    path('200/', card_2_wallet_2_crypto, name="binance_card_2_wallet_2_crypto"),
    path('300/', binance_fiat_crypto_list, name="binance_fiat_crypto_list"),
    path('400/', binance_card_2_crypto_exchanges,
         name="binance_card_2_crypto_exchanges"),
    path('500/', binance_best_crypto_exchanges,
         name="binance_best_crypto_exchanges")
]
