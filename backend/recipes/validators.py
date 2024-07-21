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
            f'Искользованы недопустипые симполы: {set(invalid_simbol)}'
        )
    return username


def validate_link(encode_id):
    if not re.match(r'[1-9]\d*', encode_id):
        raise serializers.ValidationError({'errors': 'Неправильная ссылка.'})
    return encode_id
