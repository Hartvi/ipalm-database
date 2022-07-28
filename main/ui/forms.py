from django.contrib import messages
from django import forms
from django.contrib.auth import (
    authenticate,
)

from database.models import ObjectInstance

# general vars
dataset_str = "dataset"
dataset_id_str = "dataset_id"
maker_str = "maker"
common_name_str = "common_name"
other_str = "other"
object_instance_fields = [dataset_str, dataset_id_str, maker_str, common_name_str, other_str]


class ObjectInstanceUpdateForm(forms.ModelForm):

    dataset = forms.CharField(label=dataset_str, required=False)
    dataset_id = forms.CharField(label=dataset_id_str, required=False)
    maker = forms.CharField(label=maker_str, required=False)
    common_name = forms.CharField(label=common_name_str, required=False)
    other = forms.CharField(label=other_str, required=False)

    class Meta:
        model = ObjectInstance
        fields = object_instance_fields

    def clean(self, *args, **kwargs):
        dataset = self.cleaned_data.get(dataset_str)
        dataset_id = self.cleaned_data.get(dataset_id_str)
        maker = self.cleaned_data.get(maker_str)
        common_name = self.cleaned_data.get(common_name_str)
        other = self.cleaned_data.get(other_str)
        # TODO: handle this stuff pls, mkay?
        return super(ObjectInstanceUpdateForm, self).clean(*args, **kwargs)






