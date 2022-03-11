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

            sensor_outputs: dict = data_dict["sensor_outputs"]

            # TODO: ObjectInstance ForeignKey
            measurement = Measurement.objects.create(owner=self.request.user)

            # SETUP & SETUP ELEMENT & SENSOR OUTPUT
            active_sensor_names = sensor_outputs.keys()
            sensor_modalities = {sn: list(sensor_outputs[sn].keys()) for sn in active_sensor_names}

            setup_element_dict = data_dict["setup"]
            setup_element_types = list(setup_element_dict.keys())  # gripper, arm, camera, microphone, etc
            setup_element_names = list(setup_element_dict.values())
            setup_query = Setup.objects.all()
            """
            dot notation in queries is done as follows:
            print('first setup', setup_query.filter(setup_elements__name='robotiq 2f85')[0].__dict__)
            """
            setup_exists = True
            new_setup = None

            # iterate through all setup elements present in this entry and add any new output quantities, setup elements
            for setup_element_name in setup_element_names:  # setup element names are unique
                setup_element = SetupElement.objects.filter(name=setup_element_name)
                if setup_element.exists():

                    # update the sensor quantities & bind the SensorOutput to the SetupElement
                    if setup_element_name in active_sensor_names:
                        # add new output quantities if there are any new ones:
                        oq = setup_element[0].output_quantities
                        setup_element.update(
                            output_quantities=json.dumps(
                                list(set(sensor_modalities[setup_element_name])
                                     .union(set(json.loads("[]" if oq is None else oq))))
                            )
                        )
                        sensor_output_values = sensor_outputs[setup_element_name]
                        SensorOutput.objects.create()

                    # assuming that a setup with these elements exists
                    # if so, narrow down the search, so we find that one specific setup if it exists
                    # otherwise create a new setup in the else section
                    if setup_exists:
                        setup_query = setup_query.filter(setup_elements__name=setup_element_name)
                else:
                    if setup_exists:
                        new_setup = Setup.objects.create()
                        setup_exists = False
                    new_element = SetupElement.objects.create(
                        type=setup_element_types[setup_element_names.index(setup_element_name)],
                        name=setup_element_name,
                    )
                    if setup_element_name in active_sensor_names:
                        new_element.output_quantities = json.dumps(sensor_modalities[setup_element_name])

                    new_element.save()
                    new_element.setup.add(new_setup)
                    new_element.save()
            if setup_exists:
                print("first query:", setup_query.first())
            for setup_element_name in setup_element_names:
                print("setup element name:", setup_element_name, " exists:", Setup.objects.filter(setup_elements__name=setup_element_name).exists())
            exit(1)

            # print(self.request.FILES)
            # print(self.request.__dict__)
            # print(file.__dict__)
            # with open(file.name, 'wb') as fp:
            #     fp.write(file.file.read())
        except KeyError:
            raise ParseError('Request has no resource file attached')
        # TODO either overwrite the model's create method or somehow hack this `save()`;
        #  the save can then be replaced, I think, simply by setting the serializer.instance as the measurement object
        #  and then returning the measurement object
        serializer.save(owner=self.request.user, png=file)


