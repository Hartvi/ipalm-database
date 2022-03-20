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


class SensorOutputViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SensorOutput.objects.all()
    serializer_class = SensorOutputSerializer


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


class PropertyElementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PropertyElement.objects.all()
    serializer_class = PropertyElementSerializer


class EntryViewSet(viewsets.ModelViewSet):
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )

    def perform_create(self, serializer):  # TODO: save functions
        data_items = list(self.request.data.items())
        json_data_list = list(filter(lambda x: "entry" == x[0], data_items))[0]
        data_dict = json.loads(json_data_list[1])["entry"]
        print(data_dict)
        measurement_query = Measurement.objects.filter(id=data_dict["measurement_id"])
        print(measurement_query, measurement_query.exists())
        # TODO: values, measurement object
        entry_object = serializer.save(
            owner=self.request.user,
            repository=data_dict["repository"],
            type=data_dict["type"],
            measurement=measurement_query.first()
        )
        for value in data_dict["values"]:
            PropertyElement.objects.create(
                name=value["name"],
                value=value["value"],
                std=value["std"],
                units=value["units"],
                other=value.get("other", None),
                other_file=value.get("other_file", None),
                entry=entry_object
            )


class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )

    def perform_create(self, serializer):  # TODO: save functions
        # print('performing create!!!')
        try:
            file = self.request.data['png']
            # sensor outputs:
            # print(self.request.data)
            data_items = list(self.request.data.items())
            json_data_list = list(filter(lambda x: "measurement" == x[0], data_items))[0]
            im = list(filter(lambda x: "png" == x[0], data_items))[0]
            data_dict = json.loads(json_data_list[1])

            measurement = data_dict["measurement"]
            sensor_outputs: dict = measurement["sensor_outputs"]

            # TODO: ObjectInstance ForeignKey
            # measurement = Measurement.objects.create(owner=self.request.user)

            # SETUP & SETUP ELEMENT & SENSOR OUTPUT
            sensor_output_objects = list()
            active_sensor_names = sensor_outputs.keys()
            sensor_modalities = {sn: list(sensor_outputs[sn].keys()) for sn in active_sensor_names}

            setup_element_dict = measurement["setup"]
            setup_element_types = list(setup_element_dict.keys())  # gripper, arm, camera, microphone, etc
            setup_element_names = list(setup_element_dict.values())
            setup_query = Setup.objects.all()
            # print(Setup.objects.__dict__)
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
                        sensor_output_object = SensorOutput.objects.create(
                            sensor_output=json.dumps(sensor_output_values), sensor=setup_element[0]
                        )
                        sensor_output_objects.append(sensor_output_object)
                        # ADD the measurement foreign key later

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
            setup_object = setup_query.first()
            # if setup_exists:
            #     print("first query:", setup_query.first())
            # for setup_element_name in setup_element_names:
            #     print("setup element name:", setup_element_name, " exists:",
            #           Setup.objects.filter(setup_elements__name=setup_element_name).exists())

            # ENTRY
            entry = data_dict["entry"]
            # TODO: add the Measurement to this object below
            entry_object = Entry.objects.create(
                owner=self.request.user,
                repository=entry["repository"],
                type=entry["type"]
            )
            for val in entry["values"]:
                property_element_object = PropertyElement.objects.create(
                    other=val.get("other", "[]"),
                    name=val.get("name"),
                    std=val.get("std"),
                    units=val.get("units"),
                    value=val.get("value"),
                    other_file=val.get("other_file"),  # seems to work with `None`
                    entry=entry_object
                )

            # MEASUREMENT
            # GRASP
            grasp = measurement["grasp"]
            translation = grasp["translation"]
            rotation = grasp["rotation"]
            # TODO: add the `Measurement` below
            grasp_object = Grasp.objects.create(
                rx=rotation[0],
                ry=rotation[1],
                rz=rotation[2],
                tx=translation[0],
                ty=translation[1],
                tz=translation[2],
                grasped=grasp["grasped"],
            )
        except KeyError:
            raise ParseError('Request has no resource file attached')
        object_instance = measurement["object_instance"]
        object_instance_query = ObjectInstance.objects.filter(
            owner=self.request.user,
            local_instance_id=object_instance["instance_id"],
            dataset=object_instance["dataset"]
        )
        print("query type:", type(object_instance_query))
        object_instance_object = None
        if object_instance_query.exists():
            object_instance_object = object_instance_query.filter().first()
        else:
            object_instance_object = ObjectInstance.objects.create(
                local_instance_id=object_instance["instance_id"],
                dataset=object_instance["dataset"],
                owner=self.request.user
            )
        measurement_object = serializer.save(
            owner=self.request.user,
            png=file,
            setup=setup_object,
            grasp=grasp_object,
            object_instance=object_instance_object
        )
        for soo in sensor_output_objects:
            soo.measurements = measurement_object
            soo.save()
        entry_object.measurement = measurement_object
        entry_object.save()
        grasp_object.measurement = measurement_object
        grasp_object.save()
        # print(measurement)
        # print(measurement.__dict__)



