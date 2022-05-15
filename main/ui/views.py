from django.shortcuts import render


def home_view(request):
    template_name = 'ui/home.html'
    # print("request", request)
    # print("template_name", template_name)
    return render(request=request, template_name=template_name, context={})

