from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from django.conf import settings
from django.urls import path

from . import views
from . import strings

app_name = 'database'

# Create a router and register our viewsets with it.
router = SimpleRouter()
for v, u, b in zip(strings.viewset_classes, strings.viewset_urls, strings.viewset_singular):
    router.register(u, eval('views.'+v), basename=b)
    # print('router registering', "ipalm/"+u, 'as', v)
# router.register(r'', views.SnippetViewSet)
# router.register(r'snippets2', views.Snippet2ViewSet)
# router.register(r'users', views.UserViewSet)

# print(router.__dict__)
# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
# print("rest urls:",include(router.urls))
urlpatterns = [
    path('rest/', include(router.urls)),
    path('rest/', views.api_root, name='api-root'),
]
# print("database url patterns:", urlpatterns)

