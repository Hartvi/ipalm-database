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
            meas_img = self.request.data['png']
            # sensor outputs:
            # print(self.request.data)
            data_items = list(self.request.data.items())
            json_data_list = list(filter(lambda x: "measurement" == x[0], data_items))[0]

            im = list(filter(lambda x: "png" == x[0], data_items))[0]
            data_dict = json.loads(json_data_list[1])

            measurement = data_dict["measurement"]
            entry = data_dict["entry"]
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

            setup_query_all = setup_query
            setup_candidates = []
            for setup_ in setup_query_all:
                if len(setup_.setup_elements.all()) == len(setup_element_names):
                    setup_candidates.append(setup_)
            the_setup = None
            the_setup_didnt_exist = True
            for setup_ in setup_candidates:
                count = 0
                setup_els = setup_.setup_elements.all()
                check_count = len(setup_els)
                for setup_el in setup_els:
                    # if the elements of an existing setup match those of the one just received
                    if setup_el.name in setup_element_names:
                        count += 1
                if count == check_count:
                    the_setup = setup_
                    the_setup_didnt_exist = False
                    break

            if the_setup is None:
                the_setup = Setup.objects.create()
            # iterate through all setup elements present in this entry and add any new output quantities, setup elements
            for setup_element_name in setup_element_names:  # setup element names are unique
                setup_element = SetupElement.objects.filter(name=setup_element_name)
                if setup_element.exists():
                    # update the sensor quantities & bind the SensorOutput to the SetupElement
                    the_actual_element = setup_element[0]
                    if setup_element_name in active_sensor_names:
                        # add new output quantities if there are any new ones:
                        oq = the_actual_element.output_quantities
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
                    # if the setup didnt exist, add the elements to it
                    if the_setup_didnt_exist:
                        the_actual_element.setup.add(the_setup)
                        the_actual_element.save()
                else:
                    new_element = SetupElement.objects.create(
                        type=setup_element_types[setup_element_names.index(setup_element_name)],
                        name=setup_element_name,
                    )
                    if setup_element_name in active_sensor_names:
                        new_element.output_quantities = json.dumps(sensor_modalities[setup_element_name])

                    new_element.save()
                    new_element.setup.add(the_setup)
                    new_element.save()

            # ENTRY
            # TODO: add the Measurement to this object below
            entry_object = Entry.objects.create(
                owner=self.request.user,
                repository=entry["repository"],
                type=entry["type"],
                name = entry["name"]
            )
            for val in entry["values"]:
                v = val.get("probability")
                if v is None:
                    v = val["value"]
                    u = val["units"]
                else:
                    u = val["name"]
                property_element_object = PropertyElement.objects.create(
                    other=val.get("other", "[]"),
                    name=val["name"],
                    std=val.get("std"),
                    units=u,
                    value=v,
                    other_file=val.get("other_file"),  # seems to work with `None`
                    entry=entry_object
                )

            # MEASUREMENT
            # GRASP
            grasp = measurement.get("grasp")
            if grasp:
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
            else:
                grasp_object = None
                print("no grasp: ", grasp)
            # OBJECTPOSE with relation to (wrt) robot base
            object_pose = measurement.get("object_pose")
            if object_pose:
                translation = object_pose["translation"]
                rotation = object_pose["rotation"]
                # TODO: add the `Measurement` below
                object_pose_object = ObjectPose.objects.create(
                    rx=rotation[0],
                    ry=rotation[1],
                    rz=rotation[2],
                    tx=translation[0],
                    ty=translation[1],
                    tz=translation[2],
                )
            else:
                object_pose_object = None
                print("no object_pose: ", object_pose)
        except KeyError:
            raise ParseError('Request has no resource file attached')
        object_instance = measurement["object_instance"]
        object_instance_query = ObjectInstance.objects.filter(
            owner=self.request.user,
            dataset=object_instance.get("dataset"),
            dataset_id=object_instance.get("dataset_id"),
            maker=object_instance.get("maker"),
            common_name=object_instance.get("common_name"),
            other=object_instance.get("other"),
        )

        object_instance_object = None
        if object_instance_query.exists():
            object_instance_object = object_instance_query.filter().first()
        else:
            object_instance_object = ObjectInstance.objects.create(
                owner=self.request.user,
                dataset=object_instance.get("dataset"),
                dataset_id=object_instance.get("dataset_id"),
                maker=object_instance.get("maker"),
                common_name=object_instance.get("common_name"),
                other=object_instance.get("other"),
            )
        measurement_object = serializer.save(
            owner=self.request.user,
            png=meas_img,
            setup=the_setup,
            grasp=grasp_object,
            object_pose=object_pose_object,
            object_instance=object_instance_object
        )
        for soo in sensor_output_objects:
            soo.measurements = measurement_object
            soo.save()
        entry_object.measurement = measurement_object
        entry_object.save()
        if grasp_object is not None:
            grasp_object.measurement = measurement_object
            grasp_object.save()
        if object_pose_object is not None:
            object_pose_object.measurement = measurement_object
            object_pose_object.save()

