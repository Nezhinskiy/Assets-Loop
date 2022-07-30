from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from parses_p2p.parse import get_all


def index(request):
    return get_all()
