from django.urls import include, path
from rest_framework import routers

from banks.views import tinkoff

app_name = 'parses_p2p'

urlpatterns = [
    path('1/', tinkoff, name="index"),
]
