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
    invalid_simbol = re.sub(r'[\w.@+-]+', '', username)
    if invalid_simbol:
        raise serializers.ValidationError(
            f'Искользованы недопустипые симполы: [{invalid_simbol}]'
        )
