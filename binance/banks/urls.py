from banks.views import tinkoff, wise
from django.urls import include, path
from rest_framework import routers

app_name = 'banks'

urlpatterns = [
    path('11/', tinkoff, name="tinkoff"),
    path('12/', wise, name="wise"),
]
