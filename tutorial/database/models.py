from django.db import models
from rest_framework import serializers


# class ObjectClass(models.Model):
#     name = models.CharField(max_length=100)


class ObjectInstance(models.Model):
    is_instance = models.BooleanField(default=True)
    instance_id = models.IntegerField()
    dataset = models.CharField(max_length=100, null=True)


class Setup(models.Model):
    """
    {"arm": "arm_name", "gripper": "gripper_name", "camera": "camera_model_name",
     "microphone": "microphone_model_name"}
    """
    created = models.DateTimeField(auto_now_add=True)


class SetupElement(models.Model):
    # this could be from the choices: arm, gripper, camera, depth, camera, microphone, other
    type = models.CharField(max_length=100, )
    name = models.CharField(max_length=100)
    output_quantities = models.JSONField()  # e.g. time, position, current, force, rgb, depth, bw (as in black & white)
    parameters = models.JSONField(null=True)
    setup = models.ForeignKey(Setup, on_delete=models.CASCADE, related_name='setup_elements', null=True)

    # def __str__(self):
    #     return str(self.type) + ", " + str(self.name)


class Measurement(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    png = models.ImageField(upload_to='uploads/measurements/')
    setup = models.ForeignKey(Setup, related_name='measurements', related_query_name='measurement',
                              on_delete=models.CASCADE, null=True)
    object_instance = models.ForeignKey(ObjectInstance, on_delete=models.CASCADE, related_name='measurements', null=True)
    owner = models.ForeignKey('accounts.CustomUser', related_name='measurements', related_query_name='measurement',
                              on_delete=models.PROTECT)

    class Meta:
        ordering = ['created']

    def save(self, *args, **kwargs):
        # print("saving measurement:", args, kwargs)
        super().save(*args, **kwargs)


class SensorOutput(models.Model):
    # {"time": [0.01, 0.02, ...], "position": [1, 0.99, ...], "current" : [0.05, 0.06, ...],
    #  "other_format": "png", "other": "byte_string"}
    sensor_output = models.JSONField()
    sensor = models.ForeignKey(SetupElement, on_delete=models.CASCADE, related_name='sensor_outputs', )
    measurements = models.ManyToManyField(Measurement, related_name='sensor_outputs', )


class Vector3D(models.Model):
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()


class Grasp(models.Model):
    translation = models.OneToOneField(Vector3D, on_delete=models.PROTECT, related_name='translation')
    rotation = models.OneToOneField(Vector3D, on_delete=models.PROTECT, related_name='rotation')
    grasped = models.BooleanField()
    measurement = models.OneToOneField(Measurement, related_name='grasp', on_delete=models.CASCADE)


class Entry(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    measurement = models.ForeignKey(Measurement, related_name='entries', related_query_name='entry',
                                    on_delete=models.CASCADE, null=True)
    repository = models.URLField(null=True, default='http://www.github.com')  # link to repository
    owner = models.ForeignKey('accounts.CustomUser', related_name='entries', related_query_name='entry',
                              on_delete=models.PROTECT)

    class Meta:
        ordering = ['created']

    def save(self, *args, **kwargs):
        # print("saving entry:", args, kwargs)
        # exit(1)
        super().save(*args, **kwargs)


class Property(models.Model):
    type = models.CharField(max_length=100)  # continuous, categorical, size, other
    entry = models.OneToOneField(Entry, on_delete=models.CASCADE, related_name='property')
    # maybe point to a measurement and not an object instance


class ContinuousProperty(models.Model):  # this should, I think, be possible to bind only in a OneToOneField
    quantity = models.CharField(max_length=100)
    value = models.FloatField()
    std = models.FloatField()
    units = models.CharField(max_length=100)
    other = models.JSONField(null=True)  # for friction, etc.
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='continuous')


class CategoricalProperty(models.Model):
    type = models.CharField(max_length=100)  # material, class
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='categorical')


class Category(models.Model):
    # if type is material, then: plastic, metal, etc. For class: mug, cup, etc.
    category_name = models.CharField(max_length=100)
    probability = models.FloatField()  # should be in the interval [0, 1]
    property = models.ForeignKey(CategoricalProperty, on_delete=models.CASCADE, related_name='categories')


class SizeProperty(models.Model):
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='size')


class OtherProperty(models.Model):
    name = models.CharField(max_length=100)  # size, model, mesh, half-shell, ply.
    other = models.JSONField()
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='other')
