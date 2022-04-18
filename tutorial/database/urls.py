from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.urls import path

from . import views
from . import strings

app_name = 'database'

# Create a router and register our viewsets with it.
router = DefaultRouter()
for v, u in zip(strings.viewset_classes, strings.viewset_urls):
    router.register(u, eval('views.'+v))
    # print('router registering', u, 'as', v)
# router.register(r'', views.SnippetViewSet)
# router.register(r'snippets2', views.Snippet2ViewSet)
# router.register(r'users', views.UserViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
# print("rest urls:",include(router.urls))
urlpatterns = [
    path('', include(router.urls)),
    # path('snippets/', views.SnippetViewSet.as_view({'get': 'list'})),
    # path('users/', views.UserViewSet.as_view({'get': 'list'})),
]

