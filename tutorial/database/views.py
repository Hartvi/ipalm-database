from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework import permissions, renderers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Setup, Entry
from .permissions import IsOwnerOrReadOnly
from .serializers import UserSerializer, EntrySerializer, SetupSerializer, MeasurementSerializer
from .models import Setup, Measurement, Entry


class SetupViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = Setup.objects.all()
    serializer_class = SetupSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly, )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
