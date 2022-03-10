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
    queryset = Grasp.objects.all()
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
        print('performing create!!!')
        try:
            file = self.request.data['png']
            # sensor outputs:
            # print(self.request.data)
            data_items = list(self.request.data.items())
            json_data_list = list(filter(lambda x: "measurement" == x[0], data_items))[0]
            im = list(filter(lambda x: "png" == x[0], data_items))[0]
            data_dict = json.loads(json_data_list[1])
            print(data_dict)
            sensor_outputs: dict = data_dict["sensor_outputs"]
            sensor_names = sensor_outputs.keys()
            sensor_modalities = {sn: list(sensor_outputs[sn].keys()) for sn in sensor_names}

            setup_elements = data_dict["setup"]
            setup_keys = list(setup_elements.keys())
            setup_values = list(setup_elements.values())
            print(sensor_modalities)
            for sn in sensor_names:
                sn_query = SetupElement.objects.filter(name=sn)
                if sn_query.exists():
                    element = sn_query.values()[0]
                    print(element)
                else:
                    new_element = SetupElement.objects.create(
                        type=setup_keys[setup_values.index(sn)],
                        name=sn,
                        output_quantities=json.dumps(sensor_modalities[sn]),
                    )
                    print(new_element)
            exit(1)

            # print(self.request.FILES)
            # print(self.request.__dict__)
            # print(file.__dict__)
            # with open(file.name, 'wb') as fp:
            #     fp.write(file.file.read())
        except KeyError:
            raise ParseError('Request has no resource file attached')
        serializer.save(owner=self.request.user, png=file)


