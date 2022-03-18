from django.db import models
from rest_framework import serializers


class MyBaseModel(models.Model):
    objects = models.manager.Manager()

    class Meta:
        abstract = True


class ObjectInstance(MyBaseModel):
    is_instance = models.BooleanField(default=True)
    local_instance_id = models.IntegerField()
    global_instance_id = models.IntegerField(null=True, unique=True)
    dataset = models.CharField(max_length=100, null=True)
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
    sensor_output = models.JSONField()
    sensor = models.ForeignKey(SetupElement, on_delete=models.CASCADE, related_name='sensor_outputs', )
    measurements = models.ForeignKey(Measurement, related_name='sensor_outputs', on_delete=models.CASCADE, null=True)


class Grasp(MyBaseModel):
    rx = models.FloatField(default=0)
    ry = models.FloatField(default=0)
    rz = models.FloatField(default=0)
    tx = models.FloatField(default=0)
    ty = models.FloatField(default=0)
    tz = models.FloatField(default=0)
    # translation = models.OneToOneField(Vector3D, on_delete=models.PROTECT, related_name='translation')
    # rotation = models.OneToOneField(Vector3D, on_delete=models.PROTECT, related_name='rotation')
    grasped = models.BooleanField()
    measurement = models.OneToOneField(Measurement, related_name='grasp', on_delete=models.CASCADE, null=True)


class Entry(MyBaseModel):

    created = models.DateTimeField(auto_now_add=True)
    measurement = models.ForeignKey(Measurement, related_name='entries', related_query_name='entry',
                                    on_delete=models.CASCADE, null=True)
    repository = models.URLField(null=True, default='http://www.github.com')  # link to repository
    owner = models.ForeignKey('accounts.CustomUser', related_name='entries', related_query_name='entry',
                              on_delete=models.PROTECT, null=True)
    type = models.CharField(max_length=100, null=True)  # categorical => ignore std's, continuous, others

    class Meta:
        ordering = ['created']

    def save(self, *args, **kwargs):
        # print("saving entry:", args, kwargs)
        # exit(1)
        super().save(*args, **kwargs)


class PropertyElement(MyBaseModel):  # this should, I think, be possible to bind only in a OneToOneField
    name = models.CharField(max_length=100)
    value = models.FloatField()
    std = models.FloatField()
    units = models.CharField(max_length=100)
    other = models.JSONField(null=True)  # for friction, etc.
    other_file = models.FileField(null=True)
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='property_element')


