from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .manager import CustomUserManager


class CustomUser(AbstractUser):
    avatar = models.ImageField(
        blank=True, null=True, upload_to='users/', verbose_name=_('Аватар')
    )
    email = models.EmailField(
        max_length=254, unique=True, verbose_name=_('Email')
    )
    first_name = models.CharField(_('First Name'), max_length=150)
    last_name = models.CharField(_('Last Name'), max_length=150)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
