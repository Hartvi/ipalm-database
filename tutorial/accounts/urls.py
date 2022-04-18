from django.urls import path, include
# from django.conf.urls import include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'accounts'

urlpatterns = [
    # path('', register_view, name="register"),
    path('register/', views.MyFormView.as_view(), name="register"),
]
