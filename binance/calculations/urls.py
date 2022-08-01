from django.urls import path
from calculations.views import wise

app_name = 'calculations'

urlpatterns = [
    path('3/', wise, name="calculations_wise"),
]
