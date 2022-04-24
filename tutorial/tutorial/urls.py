"""tutorial URL Configuration

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
from rest_framework.schemas import get_schema_view

from rest_framework.documentation import include_docs_urls
from django.conf.urls.static import static
from . import settings

from pathlib import Path
# from sphinx_view import DocumentationView


API_TITLE = 'Online physical properties REST API'
API_DESCRIPTION = 'A Web API for realtime uploading/downloading data for physical properties.'
schema_view = get_schema_view(title=API_TITLE)


urlpatterns = [
    # path('rest/', include('snippets.urls')),
    path('', include('ui.urls')),
    path('rest/', include('database.urls', namespace='database')),  # , namespace='database'
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('schema/', schema_view),
    path('docs/', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)),
    path('api-auth/', include('accounts.urls', namespace='accounts')),
    # path("butler-docs<path:path>",
    #      DocumentationView.as_view(
    #          json_build_dir=Path(r'C:\Users\jhart\PycharmProjects\butler\docs\build\json'),
    #          base_template_name="base.html",
    #      ),
    #      name="documentation",
    #      ),
    path(r'butler-docs/', include('docs.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
