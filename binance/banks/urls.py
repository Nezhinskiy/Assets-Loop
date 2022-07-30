from banks.views import tinkoff
from django.urls import include, path
from rest_framework import routers

app_name = 'parses_p2p'

urlpatterns = [
    path('1/', tinkoff, name="index"),
]
