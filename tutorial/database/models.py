from django.db import models
from rest_framework import serializers
from .enums import PhysicalQuantities, Units


# Signature: ListField(child=<A_FIELD_INSTANCE>, allow_empty=True, min_length=None, max_length=None)
class FloatList(serializers.ListField):
    child = serializers.FloatField()
    allow_empty = True
    # min_length = 3  # not sure if this is possible
    # max_length = 3


class StringListField(serializers.ListField):
    child = serializers.CharField()
    allow_empty = True


class Setup(models.Model):
    """
    {"arm": "arm_name", "gripper": "gripper_name", "camera": "camera_model_name",
     "microphone": "microphone_model_name"}
    """
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('accounts.CustomUser', related_name='setups', related_query_name='setup',
                              on_delete=models.PROTECT)
    arm = models.CharField()
    gripper = models.CharField()
    camera = models.CharField()
    microphone = models.CharField()
    other_sensors = models.JSONField()


class Measurement(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    png = models.ImageField(upload_to='uploads/')
    object_class = models.CharField()
    # mass, volume, density, stiffness, youngs_modulus, x, y, z, friction, material
    setup = models.ForeignKey(Setup, related_name='measurements', related_query_name='measurement',
                              on_delete=models.PROTECT)
    # {"time": [0.01, 0.02, ...], "position": [1, 0.99, ...], "current" : [0.05, 0.06, ...],
    #  "other_format": "png", "other": "byte_string"}
    sensor_output = models.JSONField()
    relative_rotation = models.JSONField()
    relative_position = models.JSONField()
    grasped = models.BooleanField()  # deez nuts
    owner = models.ForeignKey('accounts.CustomUser', related_name='measurements', related_query_name='measurement',
                              on_delete=models.PROTECT)

    class Meta:
        ordering = ['created']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Entry(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    measurement = models.ForeignKey(Measurement, related_name='entries', related_query_name='entry',
                                    on_delete=models.PROTECT)
    object_class = models.CharField()
    quantity = models.CharField(choices=PhysicalQuantities.choices())
    value = models.FloatField()
    std = models.FloatField()
    units = models.CharField(choices=Units.choices())
    algorithm = models.URLField()  # link to repository
    owner = models.ForeignKey('accounts.CustomUser', related_name='entries', related_query_name='entry',
                              on_delete=models.PROTECT)

    class Meta:
        ordering = ['object_class']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

