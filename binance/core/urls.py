from django.urls import path
from parses_p2p.views import index

app_name = 'core'

urlpatterns = [
    path('', index, name="index"),
]