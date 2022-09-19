from django.urls import path, re_path
from django.urls import path, include

from . import views

from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view

API_TITLE = 'Online physical properties REST API'
API_DESCRIPTION = 'A Web API for realtime uploading/downloading data for physical properties.'
schema_view = get_schema_view(title=API_TITLE)

app_name = 'ui'

# 'ui:database:reverse_name'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('benchmark/', views.BenchmarkView.as_view(), name='browser_home'),
    path('browser/', views.BrowserHomeView.as_view(), name='browser_home'),
    path('browser/object_instance/<int:instance_id>/', views.BrowserInstanceView.as_view(), name='browser_item'),
    # path('rest/', include('database.urls', namespace='database')),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('schema/', schema_view),
    # path('docs/', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)),
    # path('api-auth/', include('accounts.urls', namespace='accounts')),
    # path(r'butler-docs/', include('docs.urls')),
]
