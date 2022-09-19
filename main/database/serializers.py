import json
import django

from django.contrib.auth import get_user_model
from rest_framework.exceptions import ParseError
from rest_framework import serializers

from .models import *
from . import validation
from collections import OrderedDict

User = get_user_model()

"""
    class Meta:
        model = Product
        fields = ['pk', 'name', 'content', 'created', 'updated']
        expandable_fields = {
          'category': (CategorySerializer, {'many': True})
        }
"""


class UserSerializer(serializers.HyperlinkedModelSerializer):
    entries = serializers.HyperlinkedRelatedField(
        many=True, view_name='database:entry-detail', read_only=True)
    measurements = serializers.HyperlinkedRelatedField(
        many=True, view_name='database:measurement-detail', read_only=True)

    class Meta:
        model = User
        fields = '__all__'  # which fields to display on the site
        extra_kwargs = {'url': {'view_name': 'database:user-detail'}}


class GraspSerializer(serializers.HyperlinkedModelSerializer):

    measurement = serializers.HyperlinkedRelatedField(view_name='database:measurement-detail', read_only=True)

    class Meta:
        model = Grasp
        fields = '__all__'
        extra_kwargs = {'url': {'view_name': 'database:grasp-detail'}}


class ObjectPoseSerializer(serializers.HyperlinkedModelSerializer):

    measurement = serializers.HyperlinkedRelatedField(view_name='database:measurement-detail', read_only=True)

    class Meta:
        model = ObjectPose
        fields = '__all__'
        extra_kwargs = {'url': {'view_name': 'database:object_pose-detail'}}


class GraspProposalSerializer(serializers.HyperlinkedModelSerializer):

    gripper_object = serializers.HyperlinkedRelatedField(view_name='database:setup_element-detail', read_only=True)
    object_instance = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='database:object_instance-detail',  # this is predefined in the django rest framework as "[object_name]-detail"
    )

    class Meta:
        model = ObjectPose
        fields = '__all__'
        extra_kwargs = {'url': {'view_name': 'database:grasp_proposal-detail'}}


class GripperPoseSerializer(serializers.HyperlinkedModelSerializer):

    measurement = serializers.HyperlinkedRelatedField(view_name='database:measurement-detail', read_only=True)

    class Meta:
        model = GripperPose
        fields = '__all__'
        extra_kwargs = {'url': {'view_name': 'database:gripper_pose-detail'}}


class ObjectImageSerializer(serializers.HyperlinkedModelSerializer):

    # img = models.FileField(null=True)  # set with object_image.img.name = existing_name and then object_image.save()
    # object_instance = models.ForeignKey(ObjectInstance,
    #                                     on_delete=models.CASCADE, related_name='object_images', null=True)
    object_instance = serializers.HyperlinkedRelatedField(view_name='database:object_instance-detail', read_only=True)

    class Meta:
        model = ObjectImage
        fields = '__all__'
        extra_kwargs = {'url': {'view_name': 'database:object_image-detail'}}


class PropertyElementSerializer(serializers.HyperlinkedModelSerializer):

    entry = serializers.HyperlinkedRelatedField(many=False, view_name='database:entry-detail', read_only=True)

    class Meta:
        model = PropertyElement
        fields = '__all__'
        extra_kwargs = {'url': {'view_name': 'database:property_element-detail'}}


class EntrySerializer(serializers.HyperlinkedModelSerializer):
    # TODO: reverse foreignkey to property and so on

    # `source` CAN BE EMPTY IF THE VARIABLE NAME IS THE SAME, e.g. source="property"
    property_element = PropertyElementSerializer(many=True, read_only=True)

    measurement = serializers.HyperlinkedRelatedField(view_name='database:measurement-detail', read_only=True)
    owner = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='database:user-detail'
    )  # should be DataEntry.owner.username

    class Meta:
        model = Entry
        # this is basically all fields except the created date
        fields = '__all__'
        extra_kwargs = {'url': {'view_name': 'database:entry-detail'}}

    def validate(self, data):
        request = self.context['request']
        data_items = list(request.data.items())
        json_data_list = list(filter(lambda x: "entry" == x[0], data_items))[0]
        if len(json_data_list) == 0:
            raise serializers.ValidationError("`entry` key not present in request data")
        data_dict: dict = json.loads(json_data_list[1])["entry"]
        # print(data_dict)
        ## type: str, must be in [size, continuous, categorical, other]
        # measurement_id: must exist in dudes,
        # repository must be a valid url
        # values: must be non-empty and have valid fields: name, valuem std, units

        data_dict_check_result = validation.check_entry_request(data_dict)
        if data_dict_check_result:
            raise serializers.ValidationError("Entry request is missing "+data_dict_check_result)
        if data_dict["type"] not in validation.entry_types:
            raise serializers.ValidationError("entry type not in "+str(validation.entry_types))
        measurement_id = data_dict["measurement_id"]
        if not Measurement.objects.filter(id=measurement_id).exists():
            raise serializers.ValidationError("measurement with id "+str(measurement_id)+" doesn't exist!! check `/measurements` for all measurements")
        values = data_dict["values"]
        for k, value in enumerate(values):
            for i in validation.entry_value_types:
                if i in value and type(value[i]) not in validation.entry_value_types[i]:
                    raise serializers.ValidationError("values["+str(k)+"]["+i+"]: "+value[i]+" isn't of type "+str(validation.entry_value_types[i]))
        # print(data_dict)
        # raise serializers.ValidationError("testing lol")

        return data


def validate_entry(entry):
    if entry:
        if not validation.check_key_existences(entry, validation.measurement_entry_keys):
            raise serializers.ValidationError(
                "req[\"entry\"] keys do not match: " + str(validation.measurement_entry_keys) + " vs " + str(
                    entry.keys()))

        values = entry["values"]
        for value in values:
            if not validation.check_key_existences(value, validation.entry_value_key_groups):
                raise serializers.ValidationError(
                    "req[\"entry\"][\"values\"] keys do not match: " + str(entry["values"]) + " vs " + str(
                        validation.entry_value_key_groups))

        if entry["type"] != "categorical":
            for k, i in enumerate(entry["values"]):
                if "std" not in i:
                    raise serializers.ValidationError("std not in non-categorical entry " + str(k))


class SensorOutputSerializer(serializers.HyperlinkedModelSerializer):

    sensor = serializers.HyperlinkedRelatedField(view_name='database:setup_element-detail', read_only=True)
    measurement = serializers.HyperlinkedRelatedField(view_name='database:measurement-detail', read_only=True)

    class Meta:
        model = SensorOutput
        fields = '__all__'
        extra_kwargs = {'url': {'view_name': 'database:sensor_output-detail'}}


class MeasurementSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='database:user-detail'
    )  # should be DataEntry.owner.username
    setup = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='database:setup-detail'  # this is predefined in the django rest framework as "[object_name]-detail"
    )
    object_instance = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='database:object_instance-detail',  # this is predefined in the django rest framework as "[object_name]-detail"
    )
    png = serializers.ImageField(required=False)  # This has to be here in order to `post` files

    entries = EntrySerializer(many=True, read_only=True)
    grasp = GraspSerializer(many=False, read_only=True)
    object_pose = ObjectPoseSerializer(many=False, read_only=True)
    gripper_pose = GripperPoseSerializer(many=False, read_only=True)
    sensor_outputs = SensorOutputSerializer(many=True, read_only=True)

    class Meta:
        model = Measurement
        # this is basically all fields except the created date
        fields = '__all__'
        extra_kwargs = {'url': {'view_name': 'database:measurement-detail'}}

    def validate(self, data):
        # content = data.get("content", None)
        request = self.context['request']
        data_items = list(request.data.items())
        json_data_list = list(filter(lambda x: "measurement" == x[0], data_items))[0]
        if len(json_data_list) == 0:
            raise serializers.ValidationError("measurement key not present in request data")
        # print("data_items", data_items)
        im = list(filter(lambda x: "png" == x[0], data_items))
        # if len(im) == 0:
        #     raise serializers.ValidationError("png not present in request files")
        # print("json_data_list", json_data_list)
        data_dict: dict = json.loads(json_data_list[1])
        # print("data_dict", data_dict)
        # print(data_dict)
        data_dict_check_result = validation.check_measurement_request(data_dict)
        if data_dict_check_result:
            raise serializers.ValidationError("Measurement request is missing "+data_dict_check_result)
        measurement = data_dict["measurement"]
        grasp = measurement.get("grasp")
        object_pose = measurement.get("object_pose")
        gripper_pose = measurement.get("gripper_pose")
        # if not
        # if not request.FILES:
        #     raise serializers.ValidationError("Content or an Image must be provided")

        entry = data_dict.get("entry", None)
        if entry is not None:
            validate_entry(entry)
        entries = data_dict.get("entries", None)
        if entries is not None:
            for e in entries:
                validate_entry(e)
        # print("grasp: ", grasp)
        # if grasp is None:
            # print("entry[\"name\"]", entry["name"])
            # assert entry["name"] not in {"stiffness", "elasticity"}, "A grasp has to be provided for stiffness and elasticity measurements"
        if grasp is not None and len(grasp.get("translation", [])) != 0 and len(grasp.get("rotation", [])) != 0:
            if len(grasp.get("translation", [])) != 3:
                raise ParseError("len(grasp[\"translation\"]) != 3")
            if len(grasp.get("rotation", [])) != 3:
                raise ParseError("len(grasp[\"rotation\"]) != 3")
            if type(grasp.get("grasped", [])) != bool:
                raise ParseError("type(grasp[\"grasped\"]) != bool")
            if not validation.check_data_types_uniform(grasp, validation.pose_types):
                raise ParseError("grasp does not satisfy type conditions: "+str(validation.pose_types))

        if object_pose is not None and len(object_pose.get("translation", [])) != 0 and len(object_pose.get("rotation", [])) != 0:
            if len(object_pose.get("translation", [])) != 3:
                raise ParseError("len(object_pose[\"translation\"]) != 3")
            if len(object_pose.get("rotation", [])) != 3:
                raise ParseError("len(object_pose[\"rotation\"]) != 3")
            if not validation.check_data_types_uniform(object_pose, validation.pose_types):
                raise ParseError("object_pose does not satisfy type conditions: "+str(validation.pose_types))

        if gripper_pose is not None and len(gripper_pose.get("translation", [])) != 0 and len(gripper_pose.get("rotation", [])) != 0:
            if len(gripper_pose.get("translation", [])) != 3:
                raise ParseError("len(gripper_pose[\"translation\"]) != 3")
            if len(gripper_pose.get("rotation", [])) != 3:
                raise ParseError("len(gripper_pose[\"rotation\"]) != 3")
            if not validation.check_data_types_uniform(gripper_pose, validation.pose_types):
                raise ParseError("gripper_pose does not satisfy type conditions: "+str(validation.pose_types))

        object_instance = measurement["object_instance"]
        object_instance_keys = set(object_instance.keys())
        if not validation.check_set_conditions(object_instance_keys, validation.object_instance_conditions):
            raise serializers.ValidationError("measurement[\"object_instance\"] does not fulfill condition "+str(validation.object_instance_conditions))

        # if not data_dict["png"] == im[1]:
        #     raise serializers.ValidationError("uploaded image name doesnt match")
        # print("im name equals im name:", im[1])
        # print("png:", im)
        # print("data_dict:", data_dict)

        # c = request.data.copy()
        # print('request data:', type(c), c, c.__dict__, list(c.items()))
        # you dont need to set content explicitly to None
        # print('data:',data)
        # raise serializers.ValidationError("testing lol")
        return data


class SetupElementSerializer(serializers.HyperlinkedModelSerializer):

    sensor_outputs = serializers.HyperlinkedRelatedField(view_name='database:sensor_output-detail', read_only=True, many=True)

    # sensor_outputs = SensorOutputSerializer(many=True, read_only=True)

    class Meta:
        model = SetupElement
        fields = '__all__'
        extra_kwargs = {'url': {'view_name': 'database:setup_element-detail'}}


class SetupSerializer(serializers.HyperlinkedModelSerializer):

    # TODO:
    setup_elements = SetupElementSerializer(many=True, read_only=True)
    # measurements = MeasurementSerializer(many=True, read_only=True)
    # setup_elements = serializers.HyperlinkedRelatedField(view_name='setup_element-detail', read_only=True, many=True)
    measurements = serializers.HyperlinkedRelatedField(view_name='database:measurement-detail', read_only=True, many=True)

    class Meta:
        model = Setup
        fields = '__all__'
        extra_kwargs = {'url': {'view_name': 'database:setup-detail'}}


class ObjectInstanceSerializer(serializers.HyperlinkedModelSerializer):

    # TODO:
    # measurements = MeasurementSerializer(many=True, read_only=True)
    measurements = serializers.HyperlinkedRelatedField(view_name='database:measurement-detail', read_only=True, many=True)
    owner = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='database:user-detail'
    )  # should be DataEntry.owner.username

    class Meta:
        model = ObjectInstance
        fields = '__all__'
        extra_kwargs = {'url': {'view_name': 'database:object_instance-detail'}}


