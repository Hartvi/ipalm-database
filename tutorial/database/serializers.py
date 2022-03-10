import json

from django.contrib.auth import get_user_model
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
        many=True, view_name='entry-detail', read_only=True)
    measurements = serializers.HyperlinkedRelatedField(
        many=True, view_name='measurement-detail', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'id', 'entries', 'measurements')  # which fields to display on the site


class Vector3DSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Vector3D
        fields = '__all__'


class GraspSerializer(serializers.HyperlinkedModelSerializer):

    measurement = serializers.HyperlinkedRelatedField(view_name='measurement-detail', read_only=True)

    class Meta:
        model = Grasp
        fields = ('url', 'grasped', 'translation', 'rotation', 'measurement', )


class ContinuousPropertySerializer(serializers.HyperlinkedModelSerializer):

    property = serializers.HyperlinkedRelatedField(many=False, view_name='property-detail', read_only=True)

    class Meta:
        model = ContinuousProperty
        fields = '__all__'


class CategorySerializer(serializers.HyperlinkedModelSerializer):

    categoricalproperty = serializers.HyperlinkedRelatedField(many=False, view_name='categoricalproperty-detail',
                                                              read_only=True)

    class Meta:
        model = Category
        fields = '__all__'


class CategoricalPropertySerializer(serializers.HyperlinkedModelSerializer):

    property = serializers.HyperlinkedRelatedField(many=False, view_name='property-detail', read_only=True)

    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = CategoricalProperty
        fields = '__all__'


class SizePropertySerializer(serializers.HyperlinkedModelSerializer):

    property = serializers.HyperlinkedRelatedField(many=False, view_name='property-detail', read_only=True)

    class Meta:
        model = SizeProperty
        fields = '__all__'


class OtherPropertySerializer(serializers.HyperlinkedModelSerializer):

    property = serializers.HyperlinkedRelatedField(many=False, view_name='property-detail', read_only=True)

    class Meta:
        model = SizeProperty
        fields = '__all__'


class PropertySerializer(serializers.HyperlinkedModelSerializer):

    entry = serializers.HyperlinkedRelatedField(many=False, view_name='entry-detail', read_only=True)
    continuousproperty = ContinuousPropertySerializer(many=False, read_only=True, source="continuous")
    categoricalproperty = CategoricalPropertySerializer(many=False, read_only=True, source="categorical")
    sizeproperty = SizePropertySerializer(many=False, read_only=True, source="size")
    otherproperty = OtherPropertySerializer(many=False, read_only=True, source="other")

    class Meta:
        model = Property
        fields = '__all__'


class EntrySerializer(serializers.HyperlinkedModelSerializer):
    # TODO: reverse foreignkey to property and so on

    # `source` CAN BE EMPTY IF THE VARIABLE NAME IS THE SAME, e.g. source="property"
    property = PropertySerializer(many=False, read_only=True)

    measurement = serializers.HyperlinkedRelatedField(view_name='measurement-detail', read_only=True)
    owner = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='customuser-detail'
    )  # should be DataEntry.owner.username

    class Meta:
        model = Entry
        # this is basically all fields except the created date
        fields = '__all__'


class SensorOutputSerializer(serializers.HyperlinkedModelSerializer):

    """
    sensor_output = models.JSONField()
    sensor = models.ForeignKey(SetupElement, on_delete=models.CASCADE, related_name='sensor_outputs', )
    measurement = models.OneToOneField(Measurement, on_delete=models.CASCADE, related_name='sensor_outputs', )
    """
    sensor = serializers.HyperlinkedRelatedField(view_name='sensor-detail', read_only=True)
    measurement = serializers.HyperlinkedRelatedField(view_name='measurement-detail', read_only=True)

    class Meta:
        model = SensorOutput
        fields = ('url', 'sensor', 'measurement', 'sensor_output', )


class MeasurementSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='customuser-detail'
    )  # should be DataEntry.owner.username
    setup = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='setup-detail'  # this is predefined in the django rest framework as "[object_name]-detail"
    )
    png = serializers.ImageField(required=False)  # This has to be here in order to `post` files

    entries = EntrySerializer(many=True, read_only=True)
    grasp = GraspSerializer(many=False, read_only=True)
    sensor_outputs = SensorOutputSerializer(many=True, read_only=True)

    class Meta:
        model = Measurement
        # this is basically all fields except the created date
        fields = '__all__'

    def validate(self, data):
        # print("data:", data)
        # print("data dict:", data.__dict__)
        # print('validating!!!')
        content = data.get("content", None)
        request = self.context['request']
        # print('context:', self.context)
        # print(list(request.data.items()))
        data_items = list(request.data.items())
        print("data_items:", data_items)
        json_data_list = list(filter(lambda x: "measurement" == x[0], data_items))[0]
        if len(json_data_list) == 0:
            raise serializers.ValidationError("measurement key not present in request data")
        im = list(filter(lambda x: "png" == x[0], data_items))[0]
        if len(im) == 0:
            raise serializers.ValidationError("png not present in request files")
        data_dict = json.loads(json_data_list[1])
        (keys_valid, missing_keys) = validation.validate_data_fields(data_dict, 'measurement')
        if not keys_valid:
            raise serializers.ValidationError("measurement doesn't contain fields: "+str(missing_keys))
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
        if not request.FILES and not content:
            raise serializers.ValidationError("Content or an Image must be provided")
        return data

    # def create(self, validated_data):
    #     print(validated_data)
    #     return super().create(validated_data)


class SetupElementSerializer(serializers.HyperlinkedModelSerializer):

    """
    type = models.CharField(max_length=100, )
    name = models.CharField(max_length=100, )
    output_quantities = models.JSONField()  # e.g. time, position, current, force, rgb, depth, bw (as in black & white)
    parameters = models.JSONField()
    setup = models.ForeignKey(Setup, on_delete=models.CASCADE, related_name='setup_elements')
    """
    setup = serializers.HyperlinkedRelatedField(view_name='setup-detail', read_only=True)

    sensoroutputs = SensorOutputSerializer(many=True, read_only=True, source="sensor_outputs")

    class Meta:
        model = SetupElement
        fields = ('url', 'type', 'name', 'output_quantities', 'parameters', 'setup', )


class SetupSerializer(serializers.HyperlinkedModelSerializer):

    # TODO:
    setup_elements = SetupElementSerializer(many=True, read_only=True, source="setup_elements")
    measurements = MeasurementSerializer(many=True, read_only=True, source="measurements")

    class Meta:
        model = Setup
        fields = '__all__'


class ObjectInstanceSerializer(serializers.HyperlinkedModelSerializer):

    """
    class ObjectInstance(models.Model):
        is_instance = models.BooleanField(default=True)
        instance_id = models.IntegerField()
        dataset = models.CharField(max_length=100, null=True)
    """
    # TODO:
    measurements = MeasurementSerializer(many=True, read_only=True, source="measurements")

    class Meta:
        model = ObjectInstance
        fields = ('url', 'instance_id', 'dataset', )


