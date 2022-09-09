import requests
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.views import View
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
User = get_user_model()

from django import forms

# import time
from database.models import *
from . import forms

import re
import json


# import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use('Agg')  # hide plots when using 'plot'
# last_time = time.time()

use_ipalm_prefix = True
ipalm_prefix = "/ipalm"

static_prefix = "/static/"
media_prefix = "/media/"
if use_ipalm_prefix:
    static_prefix = ipalm_prefix + static_prefix
    media_prefix = ipalm_prefix + media_prefix
else:
    ipalm_prefix = ""

placeholder_img = "placeholder.png"


def dict_get_empty_to_none(d, arg):
    return d[arg] if len(re.findall(r"^\s*$", d[arg])) == 0 else None


def home_view(request):
    template_name = 'ui/home.html'

    # global last_time
    # print(len(ObjectInstance.objects.all()))
    # plt.plot([1,2,3,4], [1,2,3,4])
    # plt.savefig("C:/Users/jhart/PycharmProjects/object_database/main/site_static/home_statistics.png")  # create fig
    # if time.time() - last_time  > 3600:  # 3600 = every hour
    #     print("time.time():", time.time())
    #     last_time = time.time()

    home_context = {"measurement_len": len(Measurement.objects.all()),
                    "setup_element_len": len(SetupElement.objects.all()),
                    "object_instance_len": len(ObjectInstance.objects.all()),
                    }
    return render(request=request, template_name=template_name, context=home_context)


class BrowserHomeView(View):
    template_name = 'ui/browser_home.html'

    def get(self, request, *args, **kwargs):
        q = request.GET.get("q")
        if q is not None:
            object_instances = ObjectInstance.objects.filter(
                Q(dataset__contains=q) | Q(dataset_id__contains=q) | Q(maker__contains=q) | Q(common_name__contains=q)
            )
        else:
            object_instances = ObjectInstance.objects.all()

        paginator = Paginator(object_instances, 24)  # Show page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        page_objects = page_obj.object_list

        instance_imgs = dict()
        for o in page_objects:
            measurement_for_this_instance = Measurement.objects.filter(object_instance=o)
            number_of_pictures = 0
            imgs = list()
            for m in measurement_for_this_instance.all():  # type: Measurement
                if (".png" or ".jpg") in m.png.name and number_of_pictures < 2:
                    imgs.append(media_prefix+m.png.name)
                    number_of_pictures += 1
                sensor_output_for_this_instance = SensorOutput.objects.filter(measurements=m)
                for so in sensor_output_for_this_instance.all():  # type: SensorOutput
                    sensor_output = so.sensor_output_file
                    sensor_output_name = sensor_output.name if sensor_output.name is not None else ""
                    if sensor_output_name is not None and ((".png" or ".jpg") in sensor_output_name):
                        if len(imgs) < 3:
                            imgs.append(media_prefix+sensor_output_name)
                            number_of_pictures += 1
                        else:
                            break
            instance_imgs[o.id] = imgs if len(imgs) > 0 else [static_prefix+placeholder_img]
        len_objects = len(page_objects)
        half_index = len_objects//2
        first_half = page_objects[:half_index]
        second_half = page_objects[half_index:len_objects]
        context = {"first_half": first_half, "second_half": second_half, "page_objects": page_objects, "instance_imgs": instance_imgs, "page_obj": page_obj, "q": q}

        request.session['arguments'] = request.GET
        return render(request, self.template_name, context=context)  # {'butler_example': md_templates['butler_example']})


class BrowserInstanceView(View):
    form_class = forms.ObjectInstanceUpdateForm
    template_name = 'ui/browser_item.html'
    object_instance = None

    def get(self, request, instance_id, *args, **kwargs):
        form = self.form_class()  # initial=self.initial)
        # print(instance_id)
        # print(args, kwargs)
        object_instance = ObjectInstance.objects.filter(id=instance_id).first()
        # print(object_instance.__dict__, type(object_instance))

        form.fields[forms.common_name_str].initial = object_instance.common_name
        form.fields[forms.maker_str].initial = object_instance.maker
        form.fields[forms.dataset_str].initial = object_instance.dataset
        form.fields[forms.dataset_id_str].initial = object_instance.dataset_id
        form.fields[forms.other_str].initial = object_instance.other
        form.fields[forms.other_str].initial = object_instance.other

        measurement_for_this_instance = Measurement.objects.filter(object_instance=object_instance)
        number_of_pictures = 0
        imgs = list()
        for m in measurement_for_this_instance.all():  # type: Measurement
            if (".png" or ".jpg") in m.png.name and number_of_pictures < 5:
                imgs.append(media_prefix + m.png.name)
                number_of_pictures += 1
            sensor_output_for_this_instance = SensorOutput.objects.filter(measurements=m)
            for so in sensor_output_for_this_instance.all():  # type: SensorOutput
                sensor_output = so.sensor_output_file
                sensor_output_name = sensor_output.name if sensor_output.name is not None else ""
                if sensor_output_name is not None and ((".png" or ".jpg") in sensor_output_name):
                    if len(imgs) < 10:
                        imgs.append(media_prefix + sensor_output_name)
                        number_of_pictures += 1
                    else:
                        break
        imgs = imgs if len(imgs) > 0 else [static_prefix+placeholder_img]
        context = {"object_instance": object_instance, "imgs": imgs, "form": form, "measurements": len(Measurement.objects.filter(object_instance=object_instance))}
        context["user_exists"] = True
        context["password_matches"] = True
        kwargs_context = kwargs.get("context")
        # print("kwargs_context: ", kwargs_context)
        if kwargs_context:
            form.fields[forms.user_str].initial = kwargs_context.get("username", "")
            for k in kwargs_context:
                context[k] = kwargs_context[k]

        previous_page = request.session.get("arguments")
        if previous_page is not None:
            q = previous_page.get("q")
            q = None if q == "" else q
            page = previous_page.get("page")
            prev_url = ipalm_prefix+"/browser/"+("?" if q or page is not None else "")+(("q="+q) if q is not None else "")+("&" if q and page is not None else "")+("page="+page if page is not None else "")
            context["prev_url"] = prev_url
        else:
            prev_url = ipalm_prefix+"/browser/"
            context["prev_url"] = prev_url
        # request.session["object_instance"] = object_instance
        # self.object_instance = object_instance
        # print("self.object_instance: ", self.object_instance)
        request.session["id"] = object_instance.id
        # print("context: ", context)
        return render(request, self.template_name, context=context)  # {'butler_example': md_templates['butler_example']})

    def post(self, request, *args, **kwargs):
        # print("POST self.object_instance: ", self.object_instance)
        form = self.form_class(request.POST)
        if form.is_valid():
            clean_data = form.cleaned_data
            user = dict_get_empty_to_none(clean_data, "user")
            password = dict_get_empty_to_none(clean_data, "password")
            server_user = User.objects.filter(username=user).first()
            # print("User.objects.filter(username=user): ", User.objects.filter(username=user).first())
            if server_user is None:
                # print("kwargs: ", kwargs)
                # print("username doesnt exist yo")
                context = {"username": user, "user_exists": False}
                return self.get(request, request.session["id"], context=context)
            matchcheck = check_password(password, server_user.password)
            if not matchcheck:
                # print("username doesnt exist yo")
                context = {"username": user, "password_matches": False, "user_exists": True}
                return self.get(request, request.session["id"], context=context)
            # print("matchcheck: ", matchcheck)
            dataset = dict_get_empty_to_none(clean_data, "dataset")
            dataset_id = dict_get_empty_to_none(clean_data, "dataset_id")
            maker = dict_get_empty_to_none(clean_data, "maker")
            common_name = dict_get_empty_to_none(clean_data, "common_name")
            other = dict()
            dataset_query = Q(dataset=dataset)
            dataset_id_query = Q(dataset_id=dataset_id)
            maker_query = Q(maker=maker)
            # print("clean_data[\"maker\"]", str(dict_get_empty_to_none(clean_data, "maker")))
            common_name_query = Q(common_name=common_name)
            try:
                other = json.loads(dict_get_empty_to_none(clean_data, "other"))
                other_query = Q(other=other)
            except json.decoder.JSONDecodeError as e:
                raise forms.ValidationError("Entered JSON is invalid: "+str(e))

            instances = ObjectInstance.objects.filter(
                dataset_query & dataset_id_query & maker_query & common_name_query & other_query
            )
            update_measurements = True
            # print("request.session.get(\"id\"):", request.session.get("id"), type(request.session.get("id")))
            if len(instances) != 0:
                new_instance = instances.first()  # type: ObjectInstance
                if new_instance.id == request.session.get("id"):
                    update_measurements = False
                    # print("NOT UPDATING SINCE AN OBJECT INSTANCE ALREADY EXISTS")
                # print("found_instance: ", found_instance, "request.session.get(\"object_instance\"): ", request.session.get("object_instance"))
            else:
                new_instance = ObjectInstance.objects.create(
                    dataset=dataset, dataset_id=dataset_id, maker=maker, common_name=common_name, other=other
                )
            if update_measurements:
                # print("new_instance", new_instance)
                current_instance = ObjectInstance.objects.filter(id=request.session.get("id")).first()
                existing_measurements = Measurement.objects.filter(
                    object_instance=current_instance
                )  # type: QuerySet
                # print("number of existing measurements: ", len(existing_measurements.all()))
                for existing_measurement in existing_measurements.all():  # type: # Measurement
                    # print("new_instance.id: ", new_instance.id)
                    existing_measurement.object_instance = new_instance
                    existing_measurement.save()

            return HttpResponseRedirect("/ipalm/browser/object_instance/" + str(new_instance.id) + "/")
        return self.get(request, request.session["id"], args, kwargs)



