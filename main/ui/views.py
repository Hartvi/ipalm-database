from django.shortcuts import render
import time
from database.models import *
# import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use('Agg')  # hide plots when using 'plot'
last_time = time.time()


def home_view(request):
    template_name = 'ui/home.html'
    home_context = {"measurement_len": len(Measurement.objects.all()),
                    "setup_element_len": len(SetupElement.objects.all()),
                    "object_instance_len": len(ObjectInstance.objects.all()),
                    }

    # global last_time
    # print(len(ObjectInstance.objects.all()))
    # plt.plot([1,2,3,4], [1,2,3,4])
    # plt.savefig("C:/Users/jhart/PycharmProjects/object_database/main/site_static/home_statistics.png")  # create fig
    # if time.time() - last_time  > 3600:  # 3600 = every hour
    #     print("time.time():", time.time())
    #     last_time = time.time()

    return render(request=request, template_name=template_name, context=home_context)

