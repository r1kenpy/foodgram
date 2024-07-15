import re

from django.contrib.auth import settings
from rest_framework import serializers


def validate_username(
    username,
):
    if username == settings.INVALID_USERNAME:
        raise serializers.ValidationError(
            f'Укажите другой username: {username}'
        )
    if not re.match(r'^[\w.@+-]+\Z$', username):
        print(re.match('^[\w.@+-]+\Z$', username))
        raise serializers.ValidationError('Искользованы недопустипые симполы')
