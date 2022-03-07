import json

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

User = get_user_model()
from rest_framework import permissions, renderers, viewsets
from .permissions import IsOwnerOrReadOnly
from .serializers import *
from .models import *


class SetupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Setup.objects.all()
    serializer_class = SetupSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GraspViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Setup.objects.all()
    serializer_class = GraspSerializer


class ObjectInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ObjectInstance.objects.all()
    serializer_class = ObjectInstanceSerializer


class SetupElementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SetupElement.objects.all()
    serializer_class = SetupElementSerializer


class PropertyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer


class EntryViewSet(viewsets.ModelViewSet):
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )

    def perform_create(self, serializer):  # TODO: save functions
        serializer.save(owner=self.request.user)


class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )

    # def put(self, request, *args, **kwargs):
    #     print('LOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOL')
    #     print(request.data)
    #     file_obj = request.FILES['image']
    #     # do some stuff with uploaded file
    #     return Response(status=204)

    def perform_create(self, serializer):  # TODO: save functions
        try:
            file = self.request.data['image']
            # print(self.request.FILES)
            # print(self.request.__dict__)
            # print(file.__dict__)
            # with open(file.name, 'wb') as fp:
            #     fp.write(file.file.read())
        except KeyError:
            raise ParseError('Request has no resource file attached')
        serializer.save(owner=self.request.user, png=file)


