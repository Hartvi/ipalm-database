from django.shortcuts import render


def home_view(request):
    template_name = 'ui/home.html'
    return render(request=request, template_name=template_name, context={})

