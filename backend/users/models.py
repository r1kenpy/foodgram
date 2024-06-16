from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .manager import CustomUserManager


class CustomUser(AbstractUser):
    avatar = models.ImageField(
        blank=True, null=True, upload_to='users/', verbose_name=_('Аватар')
    )
    email = models.EmailField(unique=True, verbose_name=_('Email'))

    objects = CustomUserManager()
