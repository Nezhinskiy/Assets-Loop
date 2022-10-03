from django.http import Http404
from django.shortcuts import _get_queryset


def get_queryset_or_404(klass, *args, **kwargs):
    """
    Use filter() to return a list of objects, or raise a Http404 exception if
    the list is empty.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the filter() query.
    """
    queryset = _get_queryset(klass)
    if not hasattr(queryset, 'filter'):
        klass__name = klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        raise ValueError(
            "First argument to get_list_or_404() must be a Model, Manager, or "
            "QuerySet, not '%s'." % klass__name
        )
    target_queryset = queryset.filter(*args, **kwargs)
    if not target_queryset.exists():
        raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)
    return target_queryset
