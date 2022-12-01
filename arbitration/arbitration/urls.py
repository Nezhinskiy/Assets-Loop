"""arbitration URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.views.static import serve

urlpatterns = [
     path('select2/', include('django_select2.urls')),
     # path('admin/', admin.site.urls),
     path('', include('core.urls')),
     path('', include('crypto_exchanges.urls', namespace='crypto_exchanges')),
     path('', include('banks.urls', namespace='banks')),
     re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
     re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
 ]

urlpatterns += staticfiles_urlpatterns()
