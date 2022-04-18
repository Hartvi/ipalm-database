from django.urls import path, re_path

from . import views

app_name = 'ui'

urlpatterns = [
    path('', views.home_view, name='home'),
]
