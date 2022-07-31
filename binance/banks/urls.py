from banks.views import tinkoff
from django.urls import include, path
from rest_framework import routers

app_name = 'banks'

urlpatterns = [
    path('11/', tinkoff, name="tinkoff"),
]
