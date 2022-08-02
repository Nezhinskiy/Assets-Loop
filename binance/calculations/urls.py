from django.urls import path
from calculations.views import wise, tinkoff

app_name = 'calculations'

urlpatterns = [
    path('33/', tinkoff, name="calculations_wise"),
    path('3/', wise, name="calculations_wise"),
]
