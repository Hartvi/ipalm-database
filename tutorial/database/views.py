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
        serializer.save(owner=self.request.user)


class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )

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
            # measurement = Measurement.objects.create(owner=self.request.user)

            # SETUP & SETUP ELEMENT & SENSOR OUTPUT
            sensor_output_object = None
            active_sensor_names = sensor_outputs.keys()
            sensor_modalities = {sn: list(sensor_outputs[sn].keys()) for sn in active_sensor_names}

            setup_element_dict = data_dict["setup"]
            setup_element_types = list(setup_element_dict.keys())  # gripper, arm, camera, microphone, etc
            setup_element_names = list(setup_element_dict.values())
            setup_query = Setup.objects.all()
            # print(type(Category.objects))
            # print(type(Setup.objects))
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
                        # print(sensor_output_values)
                        # print(json.dumps(sensor_output_values))
                        sensor_output_object = SensorOutput.objects.create(
                            sensor_output=json.dumps(sensor_output_values), sensor=setup_element[0]
                        )
                        # print("sensor_output_object:", sensor_output_object)
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
            if setup_exists:
                print("first query:", setup_query.first())
            for setup_element_name in setup_element_names:
                print("setup element name:", setup_element_name, " exists:", Setup.objects.filter(setup_elements__name=setup_element_name).exists())

            # ENTRIES
            entry = data_dict["entry"]
            if "repository" not in entry:
                raise ParseError('Request has no `repository` url field')
            if "type" not in entry:
                raise ParseError('Request has no `type`<-["continuous", "categorical", "size", "other"] field')
            # TODO: add the Measurement to this object below
            entry_object = Entry.objects.create(
                owner=self.request.user,
                repository=entry["repository"],
                type=entry["type"]
            )
            for val in entry["values"]:
                property_element_object = PropertyElement.objects.create(
                    other=val.get("other", "[]"),
                    quantity=val.get("name"),
                    std=val.get("std"),
                    units=val.get("units"),
                    value=val.get("value")
                )
                if "other_file" in val:
                    # TODO: idk how to do this
                    property_element_object.other_file = val.get("other_file")
                # TODO: ADD THE `Measurement` TO THE `Entry` BELOW

            # GRASP
            grasp = data_dict["grasp"]
            if "grasped" not in grasp:
                raise ParseError('Grasp has no `grasped: bool` field')
            if "translation" not in grasp:
                raise ParseError("`translation` not in grasp")
            if "rotation" not in grasp:
                raise ParseError("`rotation` not in grasp")
            if len(grasp["translation"]) != 3:
                raise ParseError("len(grasp[\"translation\"]) != 3")
            if len(grasp["rotation"]) != 3:
                raise ParseError("len(grasp[\"rotation\"]) != 3")
            if type(grasp["grasped"]) != bool:
                raise ParseError("type(grasp[\"grasped\"]) != bool")
            translation = grasp["translation"]
            # translation_object = Vector3D.objects.create(
            #     x=translation[0],
            #     y=translation[1],
            #     z=translation[2]
            # )
            rotation = grasp["rotation"]
            # rotation_object = Vector3D.objects.create(
            #     x=rotation[0],
            #     y=rotation[1],
            #     z=rotation[2]
            # )
            # TODO: add the `Measurement` below
            grasp_object = Grasp.objects.create(
                # translation=translation_object,
                # rotation=rotation_object,
                grasped=grasp["grasped"],
            )
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
        measurement = serializer.save(owner=self.request.user, png=file)



