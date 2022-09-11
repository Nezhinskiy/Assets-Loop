from django.urls import include, path

from crypto_exchanges.views import binance_crypto, p2p_binance, card_2_fiat_2_crypto

app_name = 'crypto_exchanges'

urlpatterns = [
    path('1/', p2p_binance, name="p2p_binance"),
    path('100/', binance_crypto, name="binance_crypto"),
    path('200/', card_2_fiat_2_crypto, name="binance_card_2_fiat_2_crypto"),
]
