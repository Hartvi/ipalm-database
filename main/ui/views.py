from django.shortcuts import render
from django.core.paginator import Paginator
from django.views import View

# import time
from database.models import *


# import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use('Agg')  # hide plots when using 'plot'
# last_time = time.time()


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
        object_instances = ObjectInstance.objects.all()

        paginator = Paginator(object_instances, 24)  # Show 25 contacts per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        page_objects = page_obj.object_list

        # print(type(page_obj), page_obj.object_list)

        instance_imgs = dict()
        for o in page_objects:
            measurement_for_this_instance = Measurement.objects.filter(object_instance=o)
            number_of_pictures = 0
            # print(measurement_for_this_instance.__dict__)
            imgs = list()
            for m in measurement_for_this_instance.all():  # type: Measurement
                # print(m.__dict__)
                # print("m.png:", m.png.name)
                if (".png" or ".jpg") in m.png.name and number_of_pictures < 2:
                    imgs.append(m.png.name)
                    number_of_pictures += 1
                sensor_output_for_this_instance = SensorOutput.objects.filter(measurements=m)
                for so in sensor_output_for_this_instance.all():  # type: SensorOutput
                    sensor_output = so.sensor_output_file
                    sensor_output_name = sensor_output.name if sensor_output.name is not None else ""
                    # print(sensor_output.__dict__)
                    # print(len(sensor_output.name if sensor_output.name is not None else ""), sensor_output.name)
                    # if "jpg" in sensor_output:
                    #     print("JPG")
                    # print(so.sensor_output_file)
                    if sensor_output_name is not None and ((".png" or ".jpg") in sensor_output_name):
                        # print(sensor_output_name)
                        if len(imgs) < 3:
                            imgs.append(sensor_output_name)
                            number_of_pictures += 1
                        else:
                            break
            instance_imgs[o.id] = imgs if len(imgs) > 0 else ["placeholder.png"]
            # print(number_of_pictures)
            # print(len(measurements_for_this_instance))
            # print(o.measurement_set)
            # print(o.__dict__)
            # print(o.id)
        len_objects = len(page_objects)
        half_index = len_objects//2
        first_half = page_objects[:half_index]
        second_half = page_objects[half_index:len_objects]
        # "first_half": first_half, "second_half": second_half,
        context = {"first_half": first_half, "second_half": second_half, "page_objects": page_objects, "instance_imgs": instance_imgs, "page_obj": page_obj}
        # print("GETGETGETGETGETGETGETGETGETGETGETGETGETGETGETGETGETGETGETGETGETGETGETGETGETGETGET", request.GET.get('q'))
        # for i in instance_imgs:
        #     context[i] = instance_imgs[i]
        return render(request, self.template_name, context=context)  # {'butler_example': md_templates['butler_example']})

    # def post(self, request, *args, **kwargs):
    #     return render(request, self.template_name, {'form': None})

