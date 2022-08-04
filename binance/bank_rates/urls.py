from bank_rates.views import tinkoff, wise, BankRatesList
from django.urls import path

app_name = 'bank_rates'

urlpatterns = [
    path('11/', tinkoff, name="tinkoff"),
    path('12/', wise, name="wise"),
    path('banks/<str:name_of_bank>/',
         BankRatesList.as_view(), name='name_of_bank'),
]
