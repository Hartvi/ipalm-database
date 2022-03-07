from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


# class Organization(models.Model):
#     name = models.CharField(_('organization'), max_length=150, unique=True)


class CustomUser(AbstractUser):
    username = models.CharField(_('username'), unique=True, max_length=40)
    email = models.EmailField(_('email address'), unique=True)
    organization = models.CharField(_('organization'), max_length=150)
    # organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'organization']

    def __str__(self):
        return self.username

