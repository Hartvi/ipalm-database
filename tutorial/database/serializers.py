from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Entry, Setup

User = get_user_model()

"""
class CategorySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Category
        fields = ['pk', 'name']


class ProductSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Product
        fields = ['pk', 'name', 'content', 'created', 'updated']
        expandable_fields = {
          'category': (CategorySerializer, {'many': True})
        }
"""


class SetupSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Setup
        fields = ('url', 'arm', 'gripper', 'camera', 'microphone', 'other_sensor',
                  )


class MeasurementSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='owner-detail'
    )  # should be DataEntry.owner.username
    setup = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='setup-detail'  # this is predefined in the django rest framework as "[object_name]-detail"
    )

    class Meta:
        model = Entry
        # this is basically all fields except the created date
        fields = ('url', 'png', 'object_class', 'setup', 'sensor_output', 'relative_position', 'relative_rotation',
                  'grasped', 'owner', ) # TODO: fill in the remaining fields


class EntrySerializer(serializers.HyperlinkedModelSerializer):
    measurement = serializers.HyperlinkedRelatedField(view_name='measurement-detail')
    owner = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='owner-detail'
    )  # should be DataEntry.owner.username

    class Meta:
        model = Entry
        # this is basically all fields except the created date
        fields = ('url', 'measurement', 'object_class', 'quantity', 'value', 'std', 'units', 'algorithm', 'owner', )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    entries = serializers.HyperlinkedRelatedField(
        many=True, view_name='entry-detail', read_only=True)
    setups = serializers.HyperlinkedRelatedField(
        many=True, view_name='setup-detail', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'id', 'entries', 'setups', 'owner')  # which fields to display on the site

