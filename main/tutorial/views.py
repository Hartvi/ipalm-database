from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views import View
import markdown


# class MyView(View):
#     def get(self, request):
#         # <view logic>
#         return HttpResponse('result')

# md_templates_paths = {
#     "butler_example": "C:/Users/jhart/PycharmProjects/object_database/main/tutorial/templates/tutorial/butler_example.md",
# }

# md_templates = dict()
#
# for md_name in md_templates_paths:
#     with open(md_templates_paths[md_name], "r") as f:
#         md_templates[md_name] = markdown.markdown(f.read())


class ButlerTutorialView(View):
    template_name = 'tutorial/butler_tutorial.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, )  # {'butler_example': md_templates['butler_example']})

    # def post(self, request, *args, **kwargs):
    #     return render(request, self.template_name, {'form': None})


class TutorialHomeView(View):
    template_name = 'tutorial/tutorial_home.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, )  # {'butler_example': md_templates['butler_example']})


class ButlerFormatView(View):
    template_name = 'tutorial/butler_format.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, )  # {'butler_example': md_templates['butler_example']})


class ButlerUploadView(View):
    template_name = 'tutorial/butler_upload.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, )  # {'butler_example': md_templates['butler_example']})


class ManualUploadView(View):
    template_name = 'tutorial/manual_upload.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, )  # {'butler_example': md_templates['butler_example']})

