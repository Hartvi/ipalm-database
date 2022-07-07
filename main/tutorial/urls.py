from django.urls import path, include
# from django.conf.urls import include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'tutorial'

urlpatterns = [
    path('butler/', views.ButlerTutorialView.as_view(), name="butler_tutorial"),
    path('butler_format/', views.ButlerFormatView.as_view(), name="butler_format"),
    path('butler_upload/', views.ButlerUploadView.as_view(), name="butler_upload"),
    path('manual_upload/', views.ManualUploadView.as_view(), name="butler_upload"),
    path('', views.TutorialHomeView.as_view(), name="tutorial_home"),
]
