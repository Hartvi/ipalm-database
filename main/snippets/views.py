from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework import permissions, renderers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Snippet, Snippet2
from .permissions import IsOwnerOrReadOnly
from .serializers import SnippetSerializer, UserSerializer, Snippet2Serializer


class Snippet2ViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = Snippet2.objects.all()
    serializer_class = Snippet2Serializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly, )

    def perform_create(self, serializer):
        # print(serializer)
        # print(serializer.__dict__)
        print(self.request.__dict__)
        Snippet.objects.create(title="this is the title yo", owner=self.request.user)
        serializer.save(owner=self.request.user, snippet_id=self.request.data["snippet_id"])  # , snippet_id=self.request.snippet_id)


class SnippetViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly, )

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        # print(serializer)
        # print(serializer.__dict__)
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
