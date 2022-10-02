from django.urls import include, path

from crypto_exchanges.views import (all,
                                    binance_best_card_2_card_crypto_exchanges,
                                    binance_best_crypto_exchanges,
                                    binance_card_2_crypto_exchanges,
                                    binance_crypto, binance_fiat_crypto_list,
                                    binance_inter_exchanges_calculate,
                                    card_2_wallet_2_crypto, p2p_binance,
                                    CryptoExchangesP2PExchanges, CryptoExchangeP2PExchanges)

app_name = 'crypto_exchanges'

urlpatterns = [
    path('crypto_exchanges/banks/p2p_exchanges/',
         CryptoExchangesP2PExchanges.as_view(),
         name='crypto_exchanges_p2p_exchanges'),
    path('<str:crypto_exchange_name>/<str:bank_name>/p2p_exchanges/',
         CryptoExchangeP2PExchanges.as_view(),
         name='crypto_exchange_p2p_exchanges'),
    path('1/', p2p_binance, name="p2p_binance"),
    path('100/', binance_crypto, name="binance_crypto"),
    path('200/', card_2_wallet_2_crypto, name="binance_card_2_wallet_2_crypto"),
    path('300/', binance_fiat_crypto_list, name="binance_fiat_crypto_list"),
    path('400/', binance_card_2_crypto_exchanges,
         name="binance_card_2_crypto_exchanges"),
    path('500/', binance_best_crypto_exchanges,
         name="binance_best_crypto_exchanges"),
    path('600/', binance_best_card_2_card_crypto_exchanges,
         name="binance_best_card_2_card_crypto_exchanges"),
    path('700/', binance_inter_exchanges_calculate,
         name="binance_inter_exchanges_calculate"),
    path('1000/', all, name="all")
]
