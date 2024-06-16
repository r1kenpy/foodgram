from django.contrib.auth.models import UserManager


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
            raise ValueError('Email must be set')
        if not username:
            raise ValueError('Username must be set')
        if not first_name:
            raise ValueError('First name must be set')
        if not last_name:
            raise ValueError('Last name must be set')
        if not password:
            raise ValueError('Password must be set')

        return super().create_user(
            email, username, first_name, last_name, password, **extra_fields
        )
