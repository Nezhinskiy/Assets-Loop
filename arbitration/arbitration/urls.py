from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path('select2/', include('django_select2.urls')),
    # path('admin/', admin.site.urls),
    path('', include('core.urls')),
    re_path(
        r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}
    ),
    re_path(
        r'^static/(?P<path>.*)$', serve,
        {'document_root': settings.STATIC_ROOT}
    ),
]

urlpatterns += staticfiles_urlpatterns()
