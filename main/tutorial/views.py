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


class MyView(View):
    initial = {'key': 'value'}
    template_name = 'tutorial/butler_tutorial.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, )  # {'butler_example': md_templates['butler_example']})

    # def post(self, request, *args, **kwargs):
    #     return render(request, self.template_name, {'form': None})
