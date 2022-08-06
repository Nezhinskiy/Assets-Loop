from django.urls import include, path

from crypto_exchanges.views import binance_crypto, p2p_binance

app_name = 'parses_p2p'

urlpatterns = [
    path('1/', p2p_binance, name="p2p_binance"),
    path('100/', binance_crypto, name="binance_crypto"),
]
