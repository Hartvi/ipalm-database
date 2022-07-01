from django.urls import path, include
# from django.conf.urls import include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'tutorial'

urlpatterns = [
    path('butler/', views.MyView.as_view(), name="butler_tutorial"),
]
