from django.urls import include, path
from parses_p2p.views import index

app_name = 'parses_p2p'

urlpatterns = [
    path('1/', index, name="p2p_binance"),
]
