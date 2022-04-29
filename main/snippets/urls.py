from django.urls import path, include
# from django.conf.urls import include
from rest_framework.routers import DefaultRouter

from . import views
# from accounts.views import MyFormView

# Create a router and register our viewsets with it.
router = DefaultRouter()
# router.register(r'snippets', views.SnippetViewSet)
router.register(r'snippets', eval('views.SnippetViewSet'))
router.register(r'snippets2', views.Snippet2ViewSet)
router.register(r'users', views.UserViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
# print("rest urls:",include(router.urls))
urlpatterns = [
    path('', include(router.urls)),
    # path('snippets/', views.SnippetViewSet.as_view({'get': 'list'})),
    # path('users/', views.UserViewSet.as_view({'get': 'list'})),
]
