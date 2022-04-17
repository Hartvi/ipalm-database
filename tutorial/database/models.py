from django.db import models
from django.db.models import QuerySet
# from django.db.backends import base.Query
from rest_framework import serializers


class MyManager:
    def filter(self, *args, **kwargs) -> QuerySet:
        pass

    def all(self, *args, **kwargs) -> QuerySet:
        pass


class MyBaseModel(models.Model):
    objects = MyManager()
    # objects = models.manager.Manager()

    class Meta:
        abstract = True


class ObjectInstance(MyBaseModel):
    is_instance = models.BooleanField(default=True)
    local_instance_id = models.IntegerField(null=True)
    # global_instance_id = models.IntegerField(null=True, unique=True)  # this can be replaced by a probabilistic blockchain
    dataset = models.CharField(max_length=100, null=True)
    dataset_id = models.IntegerField(null=True)
    maker = models.CharField(max_length=100, null=True)
    common_name = models.CharField(max_length=100, null=True)
    other = models.JSONField(null=True)
    other_file = models.FileField(null=True)

    owner = models.ForeignKey('accounts.CustomUser',
                              on_delete=models.CASCADE,
                              related_name='object_instances',
                              null=True
                              )


class Setup(MyBaseModel):
    """
    {"arm": "arm_name", "gripper": "gripper_name", "camera": "camera_model_name",
     "microphone": "microphone_model_name"}
    """
    created = models.DateTimeField(auto_now_add=True)


class SetupElement(MyBaseModel):
    # this could be from the choices: arm, gripper, camera, depth, camera, microphone, other
    type = models.CharField(max_length=100, )
    name = models.CharField(max_length=100, unique=True)
    output_quantities = models.JSONField(null=True)  # e.g. time, position, current, force, rgb, depth, bw (as in black & white)
    parameters = models.JSONField(null=True)
    setup = models.ManyToManyField(Setup, related_name='setup_elements')

    # def __str__(self):
    #     return str(self.type) + ", " + str(self.name)


class Measurement(MyBaseModel):
    created = models.DateTimeField(auto_now_add=True)
    png = models.ImageField(upload_to='uploads/measurements/')
    setup = models.ForeignKey(Setup, related_name='measurements', related_query_name='measurement',
                              on_delete=models.CASCADE, null=True)
    object_instance = models.ForeignKey(ObjectInstance,
                                        on_delete=models.CASCADE, related_name='measurements', null=True)
    owner = models.ForeignKey('accounts.CustomUser', related_name='measurements', related_query_name='measurement',
                              on_delete=models.PROTECT)

    class Meta:
        ordering = ['created']

    def save(self, *args, **kwargs):
        # print("saving measurement:", args, kwargs)
        super().save(*args, **kwargs)


class SensorOutput(MyBaseModel):
    sensor_output_file = models.FileField(null=True)
    sensor_output = models.JSONField()
    sensor = models.ForeignKey(SetupElement, on_delete=models.CASCADE, related_name='sensor_outputs', )
    measurements = models.ForeignKey(Measurement, related_name='sensor_outputs', on_delete=models.CASCADE, null=True)


class Pose(MyBaseModel):
    rx = models.FloatField(default=0)
    ry = models.FloatField(default=0)
    rz = models.FloatField(default=0)
    tx = models.FloatField(default=0)
    ty = models.FloatField(default=0)
    tz = models.FloatField(default=0)

    class Meta:
        abstract = True


class Grasp(Pose):

    grasped = models.BooleanField(null=True)
    measurement = models.OneToOneField(Measurement, related_name='grasp', on_delete=models.CASCADE, null=True)


class ObjectPose(Pose):

    measurement = models.OneToOneField(Measurement, related_name='object_pose', on_delete=models.CASCADE, null=True)


class Entry(MyBaseModel):

    created = models.DateTimeField(auto_now_add=True)
    measurement = models.ForeignKey(Measurement, related_name='entries', related_query_name='entry',
                                    on_delete=models.CASCADE, null=True)
    repository = models.URLField(null=True, default='http://www.github.com')  # link to repository
    owner = models.ForeignKey('accounts.CustomUser', related_name='entries', related_query_name='entry',
                              on_delete=models.PROTECT, null=True)
    type = models.CharField(max_length=100, null=True)  # categorical => ignore std's, continuous, others
    name = models.CharField(max_length=100, null=True)  # e.g. {"type": "continuous", "name": "size"}

    class Meta:
        ordering = ['created']

    def save(self, *args, **kwargs):
        # print("saving entry:", args, kwargs)
        # exit(1)
        super().save(*args, **kwargs)


class PropertyElement(MyBaseModel):  # this should, I think, be possible to bind only in a OneToOneField
    name = models.CharField(max_length=100)
    value = models.FloatField(null=True)
    std = models.FloatField(null=True)
    units = models.CharField(max_length=100)
    other = models.JSONField(null=True)  # for friction, etc.
    other_file = models.FileField(null=True)
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='property_element')


