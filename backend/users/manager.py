from django.contrib.auth.models import UserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    def create_user(
        self,
        email=None,
        username=None,
        first_name=None,
        last_name=None,
        password=None,
        **extra_fields
    ):
        if not email:
            raise ValueError(_('Email must be set'))
        if not username:
            raise ValueError(_('Username must be set'))
        if not first_name:
            raise ValueError(_('First name must be set'))
        if not last_name:
            raise ValueError(_('Last name must be set'))
        if not password:
            raise ValueError(_('Password must be set'))

        return super().create_user(
            username=username,
            email=email,
            password=password,
            last_name=last_name,
            first_name=first_name,
            **extra_fields
        )
