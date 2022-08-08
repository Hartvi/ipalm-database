import json
import os
import re

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

User = get_user_model()
from rest_framework import permissions, renderers, viewsets
from .permissions import IsOwnerOrReadOnly
from .serializers import *
from .models import *
from main import settings

from django.shortcuts import render


param_regex = re.compile(r"param[a-z]*")


# print("STARTIN THE VIEWS YO")
# print(len(SensorOutput.objects.all()))
# for sensor_output_object in SensorOutput.objects.all():  # type: SensorOutput
#     # print(so.sensor_output)
#     sensor_output_values = sensor_output_object.sensor_output
#     # print(sensor_output_values)
#     sensor_file_name = "output" + str(sensor_output_object.id) + ".json"
#     with open(os.path.join(settings.MEDIA_ROOT, sensor_file_name), "w") as f:
#         json.dump(obj=sensor_output_values, fp=f)
#     sensor_output_object.sensor_output_large = sensor_file_name
#     sensor_output_object.save()


def api_root(request):
    template_name = 'database/api-root.html'
    return render(request=request, template_name=template_name, context={})


class SetupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Setup.objects.all()
    serializer_class = SetupSerializer


class SensorOutputViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SensorOutput.objects.all()
    serializer_class = SensorOutputSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ObjectPoseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ObjectPose.objects.all()
    serializer_class = ObjectPoseSerializer


class GripperPoseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GripperPose.objects.all()
    serializer_class = GripperPoseSerializer


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
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )
    permission_classes = (permissions.AllowAny, )

    def perform_create(self, serializer):  # TODO: save functions
        data_items = list(self.request.data.items())
        json_data_list = list(filter(lambda x: "entry" == x[0], data_items))[0]
        data_dict = json.loads(json_data_list[1])["entry"]
        measurement_query = Measurement.objects.filter(id=data_dict["measurement_id"])
        # TODO: values, measurement object
        entry_object = serializer.save(
            # owner=self.request.user,
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
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )
    permission_classes = (permissions.AllowAny, )

    def perform_create(self, serializer):  # TODO: save functions
        for sensor_output_object in SensorOutput.objects.all():  # type: SensorOutput
            # print(so.sensor_output)
            sensor_output_values = sensor_output_object.sensor_output
            # print(sensor_output_values)
            sensor_file_name = "output" + str(sensor_output_object.id) + ".json"
            with open(os.path.join(settings.MEDIA_ROOT, sensor_file_name), "w") as f:
                json.dump(obj=sensor_output_values, fp=f)
            sensor_output_object.sensor_output_large = sensor_file_name
            sensor_output_object.save()
        # try:
        # for k in self.request.data:
        #     print(k, " : ", self.request.data[k])
        # meas_img = self.request.data['png']
        # # sensor outputs:
        # # print(self.request.data)
        # data_items = list(self.request.data.items())
        # json_data_list = list(filter(lambda x: "measurement" == x[0], data_items))[0]
        #
        # im = list(filter(lambda x: "png" == x[0], data_items))[0]
        # data_dict = json.loads(json_data_list[1])
        # "object_instance .*file.*", "measurement {setup_element} {quantity}", "entry {property_element} .*file.*"
        lvl1_key_radicals = ["object_instance", "measurement", "entry"]
        request_data = self.request.data
        file_keys = request_data.keys()
        # print("file_keys:", file_keys)
        data_dict = json.loads(request_data["measurement"])

        measurement_dict = data_dict["measurement"]
        entry_dict = data_dict.get("entry")
        sensor_output_dict: dict = measurement_dict["sensor_outputs"]

        # SETUP & SETUP ELEMENT & SENSOR OUTPUT
        sensor_output_objects = list()
        active_sensor_names = sensor_output_dict.keys()
        sensor_modalities = dict()
        sensor_output_parameters = dict()
        for sn in active_sensor_names:
            # this shouldnt exist:
            single_sensor_output = sensor_output_dict[sn]
            sensor_quantities = list(single_sensor_output.keys())
            param_key_str = None
            for sensor_quantity in sensor_quantities:
                param_key_match = param_regex.search(sensor_quantity)
                if param_key_match is not None:
                    # sensor_output_parameters[sn] = dict()
                    # the quantity should be param[a-z]*
                    sensor_output_parameters[sn] = single_sensor_output[sensor_quantity]
                    # print("found param key: ", param_key_match)
                    param_key_str = param_key_match.group()
            sensor_modalities[sn] = list(filter(lambda x: x != param_key_str, sensor_quantities))
            # print("incoming sensor modalities: ", sensor_modalities[sn])

        setup_element_dict = measurement_dict["setup"]
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
                the_actual_element = setup_element[0]  # type: SetupElement
                if setup_element_name in active_sensor_names:
                    # add new output quantities if there are any new ones:
                    # NOTE: the_actual_element.name is the same as setup_element_name
                    original_quantities = the_actual_element.output_quantities
                    setup_element.update(
                        output_quantities=json.dumps(
                            list(set(sensor_modalities[setup_element_name])
                                 .union(set(json.loads("[]" if original_quantities is None else original_quantities))))
                        )
                    )
                    # print("all quantities for sensor", setup_element_name, ": ", list(set(sensor_modalities[setup_element_name])
                    #      .union(set(json.loads("[]" if original_quantities is None else original_quantities)))))
                    # print("new quantities for sensor", setup_element_name, ": ", sensor_modalities[setup_element_name])
                    sensor_output_values = sensor_output_dict[setup_element_name]
                    p = re.compile(r"^[a-zA-Z]:")
                    for q in sensor_output_values:
                        if type(sensor_output_values[q]) != str:
                            continue
                        forward_slash_file_path = sensor_output_values[q].replace("\\", r"/")  # type   : str
                        unix_file_path = p.sub("", forward_slash_file_path)
                        if os.path.isabs(forward_slash_file_path):
                            new_file_name = os.path.basename(forward_slash_file_path)
                            sensor_output_values[q] = new_file_name
                        elif os.path.isabs(unix_file_path):
                            new_file_name = os.path.basename(forward_slash_file_path)
                            sensor_output_values[q] = new_file_name
                        # print("q", q, "sensor_output_values[q]", sensor_output_values[q])

                    sensor_output_object = SensorOutput.objects.create(
                        sensor=setup_element[0],
                        parameters=json.dumps(sensor_output_parameters.get(setup_element_name, {}))
                    )
                    # print(len(json.dumps(sensor_output_values)))
                    # print(sensor_output_object.id)
                    sensor_file_name = "output"+str(sensor_output_object.id)+".json"
                    with open(os.path.join(settings.MEDIA_ROOT, sensor_file_name), "w") as f:
                        json.dump(obj=sensor_output_values, fp=f)
                    sensor_output_object.sensor_output_large = sensor_file_name
                    sensor_output_object.save()
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
        if entry_dict is not None:
            entry_object = Entry.objects.create(
                owner=self.request.user,
                repository=entry_dict["repository"],
                type=entry_dict["type"],
                name=entry_dict["name"]
            )
            property_element_objects = list()
            for val in entry_dict["values"]:
                v = val.get("probability")
                if v is None:
                    # print("val:", val)
                    v = val.get("value", val.get("mean"))  # TODO: this is sometimes not present
                    u = val["units"]
                    if u is None:
                        # TODO: convert SI to the actual units based on the name of the quantity, e.g. kg m^-3 for density
                        u = "SI"
                else:
                    u = val["name"]
                property_element_object = PropertyElement.objects.create(
                    other=val.get("other", "[]"),
                    name=val["name"],
                    std=val.get("std"),
                    units=u,
                    value=v,
                    other_file=val.get("other_file"),
                    entry=entry_object
                )
                property_element_objects.append(property_element_object)

        # MEASUREMENT
        # GRASP
        grasp = measurement_dict.get("grasp")
        grasp_object = None
        if grasp:
            translation = grasp.get("translation")  # type: list
            rotation = grasp.get("rotation")  # type: list
            grasped = grasp.get("grasped")
            if translation is not None and rotation is not None and grasped is not None:
                # TODO: add the `Measurement` below
                grasp_object = Grasp.objects.create(
                    rx=rotation[0],
                    ry=rotation[1],
                    rz=rotation[2],
                    tx=translation[0],
                    ty=translation[1],
                    tz=translation[2],
                    grasped=grasp.get("grasped")
                )
        # OBJECTPOSE with relation to (wrt) robot base
        object_pose = measurement_dict.get("object_pose")
        object_pose_object = None
        if object_pose:
            translation = object_pose.get("translation")  # type: list
            rotation = object_pose.get("rotation")  # type: list
            if translation and rotation:
                # TODO: add the `Measurement` below
                object_pose_object = ObjectPose.objects.create(
                    rx=rotation[0],
                    ry=rotation[1],
                    rz=rotation[2],
                    tx=translation[0],
                    ty=translation[1],
                    tz=translation[2],
                )
        gripper_pose = measurement_dict.get("gripper_pose")
        gripper_pose_object = None
        if gripper_pose:
            translation = gripper_pose.get("translation")  # type: list
            rotation = gripper_pose.get("rotation")  # type: list
            grasped = gripper_pose.get("grasped")
            # print(translation, rotation, grasped)
            if translation is not None and rotation is not None and grasped is not None:
                # TODO: add the `Measurement` below
                gripper_pose_object = GripperPose.objects.create(
                    rx=rotation[0],
                    ry=rotation[1],
                    rz=rotation[2],
                    tx=translation[0],
                    ty=translation[1],
                    tz=translation[2],
                    grasped=grasped
                )
        # except KeyError:
        #     raise ParseError('Request has no resource file attached')
        object_instance = measurement_dict["object_instance"]  # type: dict
        # print(object_instance)
        # print(object_instance.get("dataset"),str(object_instance.get("dataset_id")),object_instance.get("maker"),object_instance.get("common_name"),object_instance.get("other"))
        object_instance_query = ObjectInstance.objects.filter(
            # owner=self.request.user,
            dataset=object_instance.get("dataset"),  # TODO: COMPARING NONE TO NULL IS FALSE AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
            dataset_id=object_instance.get("dataset_id"),
            maker=object_instance.get("maker"),
            common_name=object_instance.get("common_name"),
            # other=object_instance.get("other", {}),
        )
        # print(len(object_instance_query.all()))
        # print(object_instance_query.first().other == None)

        object_instance_object = None
        if object_instance_query.exists():
            object_instance_object = object_instance_query.first()  # type: ObjectInstance
            # merge the "other" json fields
            existing_other_dict = object_instance_object.other
            new_other_dict = object_instance.get("other", {})
            # print(existing_other_dict)
            for k in new_other_dict:
                v = new_other_dict[k]
                new_k = k  # type: str
                i = 1
                if new_k in existing_other_dict:
                    new_k = new_k + str(i)
                    while new_k in existing_other_dict:
                        new_k = new_k.replace(str(i), str(i+1))  # should start duplicates with 2
                        i += 1
                    existing_other_dict[new_k] = v
                    # print("if", existing_other_dict)
                else:
                    existing_other_dict[k] = v
                    # print("else", existing_other_dict)
            # print("after",existing_other_dict)
            object_instance_object.other = existing_other_dict
            object_instance_object.save()
        else:
            object_instance_object = ObjectInstance.objects.create(
                # owner=self.request.user,
                dataset=object_instance.get("dataset"),
                dataset_id=object_instance.get("dataset_id"),
                maker=object_instance.get("maker"),
                common_name=object_instance.get("common_name"),
                other=object_instance.get("other", {}),
            )
        measurement_object = serializer.save(
            owner=self.request.user,
            # png=meas_img,
            setup=the_setup,
            grasp=grasp_object,
            object_pose=object_pose_object,
            gripper_pose=gripper_pose_object,
            object_instance=object_instance_object
        )
        for soo in sensor_output_objects:
            # print(soo.sensor.name)
            soo.measurements = measurement_object
            soo.save()
        if entry_dict is not None:
            entry_object.measurement = measurement_object
            entry_object.save()
        if grasp_object is not None:
            grasp_object.measurement = measurement_object
            grasp_object.save()
        if object_pose_object is not None:
            object_pose_object.measurement = measurement_object
            object_pose_object.save()
        if gripper_pose_object is not None:
            gripper_pose_object.measurement = measurement_object
            gripper_pose_object.save()

        """ e.g. 
        measurement intel_d435 pointcloud_file, 
        measurement object_instance, 
        entry values property_element_name, 
        measurement png
        """
        fk_levels = list()
        # print("file_keys:", file_keys)
        for fk in file_keys:
            fk_split = fk.split(" ")
            fk_split_len = len(fk_split)
            while len(fk_levels) < fk_split_len:
                fk_levels.append(list())
            fk_levels[fk_split_len-1].append(fk_split)
        # print("fk_levels", fk_levels)
        if len(fk_levels) >= 2:
            for fk_split in fk_levels[1]:
                if fk_split[0] == "measurement":
                    if fk_split[1] == "png":
                        measurement_object.png = request_data[" ".join(fk_split)]
                        measurement_object.save()
                    elif fk_split[1] == "object_instance":
                        object_instance_object.other_file = request_data[" ".join(fk_split)]
                        object_instance_object.save()
            if len(fk_levels) >= 3:
                for fk_split in fk_levels[2]:
                    # e.g. measurement intel_d435 pointcloud_file
                    potential_sensor_output_objects = list(filter(lambda x: x.sensor.name == fk_split[1], sensor_output_objects))
                    if fk_split[0] == "measurement" and len(potential_sensor_output_objects) == 1:
                        sensor_output_object: SensorOutput = potential_sensor_output_objects[0]
                        sensor_output_object.sensor_output_file = request_data[" ".join(fk_split)]
                        # print("sensor_output_object.sensor_output_file: ", request_data[" ".join(fk_split)], "type: ", type(request_data[" ".join(fk_split)]))
                        sensor_output_object.save()
                    potential_property_elements = list(filter(lambda x: x.name == fk_split[2], property_element_objects))
                    if fk_split[0] == "entry" and fk_split[1] == "values" and len(potential_property_elements) == 1:
                        property_element_object: PropertyElement = potential_property_elements[0]
                        property_element_object.other_file = request_data[" ".join(fk_split)]
                        property_element_object.save()

