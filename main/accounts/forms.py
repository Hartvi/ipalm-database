from django.contrib import messages
from django import forms
from django.contrib.auth import (
    authenticate,
    get_user_model

)

User = get_user_model()

# from .models import Organization
# User = CustomUser


class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(label='Username')
    email = forms.EmailField(label='Email')
    organization = forms.CharField(label='Organization')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm password')

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'organization',
            'password',
            'confirm_password',
        ]

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        # organization = self.cleaned_data.get('organization')
        organization_str = self.cleaned_data.get('organization')
        # print(organization_str)
        # organization = Organization.objects.filter(name=organization_str).first()
        # print(organization)
        # if organization is None:
        #     organization = Organization.objects.create(name=organization_str)
        # print(organization)
        # print(organization.customuser_set.__dict__)
        # self.cleaned_data.update({'organization': organization})
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        email_check = User.objects.filter(email=email)
        if email_check.exists():
            raise forms.ValidationError("This email is already registered.")
        username_check = User.objects.filter(username=username)
        if username_check.exists():
            raise forms.ValidationError("This user is already registered.")
        return super(UserRegisterForm, self).clean(*args, **kwargs)
