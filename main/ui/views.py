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
from main import settings

# import time
from database.models import *
from . import forms

import os
import re
import json
import random


# import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use('Agg')  # hide plots when using 'plot'
# last_time = time.time()

use_ipalm_prefix = True
# use_ipalm_prefix = False
ipalm_prefix = "/ipalm"

static_prefix = "/static/"
media_prefix = "/media/"

if not use_ipalm_prefix:
    ipalm_prefix = ""

static_prefix = ipalm_prefix + static_prefix
media_prefix = ipalm_prefix + media_prefix
# print("media_prefix", media_prefix)

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

    # Measurement.objects.filter()
    object_instances = ObjectInstance.objects.all()
    instance_ids_for_context = list()
    image_links = dict()

    for o in object_instances:
        oid = o.id
        associated_imgs = ObjectImage.objects.filter(object_instance__id=oid)
        if len(associated_imgs) > 0:
            random_ass_image = random.choice(associated_imgs)  # type: ObjectImage
            image_link = media_prefix + random_ass_image.img.name
            image_links[oid] = image_link
            instance_ids_for_context.append(oid)


    home_context = {"measurement_len": len(Measurement.objects.all()),
                    "setup_element_len": len(SetupElement.objects.all()),
                    "object_instance_len": len(ObjectInstance.objects.all()),
                    "object_ids": instance_ids_for_context,
                    "image_links": image_links
                    }
    return render(request=request, template_name=template_name, context=home_context)


class BenchmarkView(View):
    template_name = 'ui/benchmark.html'

    def get(self, request, *args, **kwargs):
        # source quantity, target quantity
        # source_quantity = request.GET.get("source")
        # target_quantity = request.GET.get("target")
        # print(target_quantity, source_quantity)
        # if target_quantity is None:
        #     target_entries = Entry.objects.all()
        # else:
        #     all_entries = Entry.objects.filter(Q(name__contains=target_quantity))
        # for entry in all_entries:

        # Entry.object.filter(Q(name__contains=''))
        context = {}
        setup_elements = SetupElement.objects.all()
        object_instances = ObjectInstance.objects.all()
        entries = Entry.objects.all()
        # for o in object_instances:
        context["setup_elements"] = setup_elements
        context["object_instances"] = object_instances
        context["entries"] = entries
        # if target_quantity is None:
        #     context["target_quantity"] = False
        return render(request, self.template_name, context=context)  # {'butler_example': md_templates['butler_example']})


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

        # TODO: sort by the number of images the objects have

        objects_with_images = list()
        objects_without_images = list()
        instance_imgs = dict()
        for o in object_instances:
            instance_imgs[o.id] = list(map(lambda x: media_prefix + x.img.name, ObjectImage.objects.filter(object_instance=o)[:3]))
            if len(instance_imgs[o.id]) > 0:
                # print("image url: ", instance_imgs[o.id][0])
                objects_with_images.append(o)
            else:
                objects_without_images.append(o)
        display_objects = objects_with_images + objects_without_images
        paginator = Paginator(display_objects, 24)  # Show page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        page_objects = page_obj.object_list

        # instance_imgs
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

        # instance_imgs = dict()
        # for o in object_instances:
        #     instance_imgs[o.id] = list(map(lambda x: x.img.name, ObjectImage.objects.filter(object_instance__id=oid)[:10]))
        # measurement_for_this_instance = Measurement.objects.filter(object_instance=object_instance)
        # number_of_pictures = 0


        associated_imgs = ObjectImage.objects.filter(object_instance__id=object_instance.id)
        ten_imgs = associated_imgs[:min(10, len(associated_imgs))]
        imgs = list(map(lambda x: media_prefix + x.img.name, ten_imgs   ))
        # print("len(imgs): ", len(imgs))
        # for m in measurement_for_this_instance.all():  # type: Measurement
        #     if (".png" or ".jpg") in m.png.name and number_of_pictures < 5:
        #         imgs.append(media_prefix + m.png.name)
        #         number_of_pictures += 1
        #     sensor_output_for_this_instance = SensorOutput.objects.filter(measurements=m)
        #     for so in sensor_output_for_this_instance.all():  # type: SensorOutput
        #         sensor_output = so.sensor_output_file
        #         sensor_output_name = sensor_output.name if sensor_output.name is not None else ""
        #         if sensor_output_name is not None and ((".png" or ".jpg") in sensor_output_name):
        #             if len(imgs) < 10:
        #                 imgs.append(media_prefix + sensor_output_name)
        #                 number_of_pictures += 1
        #             else:
        #                 break
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


# try:
#     with open(os.path.join(settings.BASE_DIR, "object_instances.json"), "r+") as fp:
#         cached_instances = json.load(fp)
#         # print("using cached instances")
# except:
#     with open(os.path.join(settings.BASE_DIR, "object_instances.json"), "w") as fp:
#         pass
cached_instances = dict()



# for o in ObjectInstance.objects.all():  # type: ObjectInstance
#     ObjectImage.objects.filter(object_instance__id=o.id).delete()

# for o in ObjectImage.objects.all():
#     o.delete()
#
# for o in ObjectInstance.objects.all():  # type: ObjectInstance
#     oid = o.id
#     # if str(oid) not in cached_instances:
#     #     cached_instances[oid] = True
#     # else:
#     #     continue
#     imgs = ObjectImage.objects.filter(object_instance__id=oid)
#     # print("object instance id:", oid, " number of images:", len(imgs))
#     if len(imgs) > 0:
#         o.has_image = True
#         o.save()
#     measurement_for_this_instance = Measurement.objects.filter(object_instance__id=oid)
#     # number_of_pictures = 0
#     # imgs = list()
#     for m in measurement_for_this_instance.all():  # type: Measurement
#         png_name = m.png.name
#         if ".png" in png_name or ".jpg" in png_name:
#             object_image_object = ObjectImage.objects.create()  # type: ObjectImage
#             object_image_object.img.name = png_name
#             object_image_object.object_instance = o
#             object_image_object.save()
#             # imgs.append(media_prefix+m.png.name)
#             # number_of_pictures += 1
#         sensor_output_for_this_instance = SensorOutput.objects.filter(measurements=m)
#         for so in sensor_output_for_this_instance.all():  # type: SensorOutput
#             sensor_output = so.sensor_output_file
#             sensor_output_name = sensor_output.name if sensor_output.name is not None else ""
#             if sensor_output_name is not None and (".png" in sensor_output_name or ".jpg" in sensor_output_name):
#                 # print("sensor_output_name: ", sensor_output_name)
#                 object_image_object = ObjectImage.objects.create()  # type: ObjectImage
#                 object_image_object.img.name = sensor_output_name  # TODO: media_prefix + img_name to get the link!!!
#                 object_image_object.object_instance = o
#                 # print(object_image_object, object_image_object.img, object_image_object.object_instance)
#                 object_image_object.save()
#                 # imgs.append(media_prefix + sensor_output_name)
#                 # number_of_pictures += 1
#             # if sensor_output_name is not None and ((".png" or ".jpg") in sensor_output_name):
#             #     if len(imgs) < 3:
#             #         imgs.append(media_prefix+sensor_output_name)
#             #         number_of_pictures += 1
#             #     else:
#             #         break
#     # instance_imgs[o.id] = imgs if len(imgs) > 0 else [static_prefix+placeholder_img]


# with open(os.path.join(settings.BASE_DIR, "object_instances.json"), "r+") as fp:
    # json.dump(obj=cached_instances, fp=fp)

