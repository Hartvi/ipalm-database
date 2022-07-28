from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponseRedirect

# from .models import Organization

from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout
)

from .forms import UserRegisterForm

import logging
logger = logging.getLogger(__name__)


class MyFormView(View):
    form_class = UserRegisterForm
    # initial = {}
    template_name = 'signup.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()  # initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        next = request.GET.get('next')  # how to read/write to this variable??
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            user.set_password(password)
            user.save()
            new_user = authenticate(username=user.username, password=password)
            login(request, new_user)
            if next:
                return redirect(next)
            return HttpResponseRedirect('/ipalm/')

        return render(request, self.template_name, {'form': form})


# def register_view(request):
#     form = UserRegisterForm(request.POST or None)
#     if form.is_valid():
#         user = form.save(commit=False)
#         password = form.cleaned_data.get('password')
#         user.set_password(password)
#         user.save()
#         new_user = authenticate(username=user.username, password=password)
#         login(request, new_user)
#         return redirect('/ipalm/')
#
#     context = {
#         'form': form,
#     }
#     return render(request, "signup.html", context)


