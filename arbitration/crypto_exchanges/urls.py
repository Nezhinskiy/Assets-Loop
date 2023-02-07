from django.urls import include, path
from django.views.generic.base import TemplateView

from crypto_exchanges.views import (
    CryptoExchangeInternalExchanges, CryptoExchangeP2PExchanges,
    CryptoExchangesInternalExchanges, CryptoExchangesP2PExchanges,
    InterExchangesAPIView, InterExchangesList, InterExchangesListNew, all,
    binance_best_card_2_card_crypto_exchanges, binance_best_crypto_exchanges,
    binance_card_2_crypto_exchanges, binance_crypto, binance_fiat_crypto_list,
    binance_inter_exchanges_calculate, card_2_wallet_2_crypto,
    complex_binance_tinkoff_inter_exchanges_calculate,
    complex_binance_wise_inter_exchanges_calculate,
    get_tinkoff_p2p_binance_exchanges, get_wise_p2p_binance_exchanges,
    simpl_binance_tinkoff_inter_exchanges_calculate,
    simpl_binance_wise_inter_exchanges_calculate)

app_name = 'crypto_exchanges'

urlpatterns = [
    path('crypto_exchanges/internal_crypto_exchanges/',
         CryptoExchangesInternalExchanges.as_view(),
         name='crypto_exchanges_internal_exchanges'),
    path('<str:crypto_exchange_name>/internal_crypto_exchanges/',
         CryptoExchangeInternalExchanges.as_view(),
         name='crypto_exchange_internal_exchanges'),
    path('crypto_exchanges/banks/p2p_exchanges/',
         CryptoExchangesP2PExchanges.as_view(),
         name='crypto_exchanges_p2p_exchanges'),
    path('<str:crypto_exchange_name>/<str:bank_name>/p2p_exchanges/',
         CryptoExchangeP2PExchanges.as_view(),
         name='crypto_exchange_p2p_exchanges'),
    path('inter-exchanges/',
         InterExchangesList.as_view(),
         name='InterExchangesList'),
    path('',
         InterExchangesListNew.as_view(),
         name='InterExchangesListNew'),
    path('data/', InterExchangesAPIView.as_view(), name='inter-exchanges_data'),
    path('1/', get_tinkoff_p2p_binance_exchanges, name="get_tinkoff_p2p_binance_exchanges"),
    path('2/', get_wise_p2p_binance_exchanges, name="get_wise_p2p_binance_exchanges"),
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
    path('1000/', all, name="all"),
    path('simpltin/', simpl_binance_tinkoff_inter_exchanges_calculate,
         name="simpl_binance_tinkoff_inter_exchanges_calculate"),
    path('simplwise/', simpl_binance_wise_inter_exchanges_calculate,
         name="simpl_binance_wise_inter_exchanges_calculate"),
    path('complextin/', complex_binance_tinkoff_inter_exchanges_calculate,
         name="complex_binance_tinkoff_inter_exchanges_calculate"),
    path('complexwise/', complex_binance_wise_inter_exchanges_calculate,
         name="simpl_binance_tinkoff_inter_exchanges_calculate"),
    path('z/', InterExchangesList.as_view(),
         name="z"),
]
