"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.schemas import get_schema_view

from rest_framework.documentation import include_docs_urls
from django.conf.urls.static import static
from . import settings

from pathlib import Path
# from sphinx_view import DocumentationView


API_TITLE = 'Online physical properties REST API'
API_DESCRIPTION = 'A Web API for realtime uploading/downloading data for physical properties.'
schema_view = get_schema_view(title=API_TITLE)

# duplicate_url_prefixes = ["ipalm/", ]
duplicate_url_prefix = "ipalm/"
duplicate_namespace_prefix = "ipalm_"

urlpatterns = [
    path('', include('ui.urls')),  # relative, i.e. relative '/*******' => ipalm/*******
    path('rest/', include('database.urls', namespace='database')),  # absolute felk.cvut.cz/ipalm/rest
    # path(duplicate_url_prefix, include('database.urls', namespace='database')),  # absolute felk.cvut.cz/ipalm/rest
    # path('', include('database.urls', namespace=duplicate_namespace_prefix + 'database')),  # absolute felk.cvut.cz/rest

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('schema/', schema_view),
    path('docs/', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)),
    path('api-auth/', include('accounts.urls', namespace='accounts')),
    path('butler-docs/', include('docs.urls')),
    path('tutorial/', include('tutorial.urls', namespace='tutorial')),
    # path(duplicate_url_prefix, include('ui.urls')),  # relative, i.e. relative '/*******' => ipalm/*******
    path(duplicate_url_prefix + 'api-auth/', include('rest_framework.urls', namespace=duplicate_namespace_prefix + 'rest_framework')),
    path(duplicate_url_prefix + 'schema/', schema_view),
    path(duplicate_url_prefix + 'docs/', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)),
    path(duplicate_url_prefix + 'api-auth/', include('accounts.urls', namespace=duplicate_namespace_prefix+'accounts')),
    path(duplicate_url_prefix + 'butler-docs/', include('docs.urls')),
    path(duplicate_url_prefix + 'tutorial/', include('tutorial.urls', namespace=duplicate_namespace_prefix+'tutorial')),
    # in case redirects are needed
    # path(r'^.*$', RedirectView.as_view(url='<url_to_home_view>', permanent=False), name='index')
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# print(path(r'butler-docs/', include('docs.urls')).__dict__)
# for duplicate_url_prefix in duplicate_url_prefixes:
#     urlpatterns
