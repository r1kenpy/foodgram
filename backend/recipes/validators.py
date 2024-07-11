import re

from rest_framework import serializers


def validate_username(
    username,
):
    if username == 'me':
        raise serializers.ValidationError('Укажите другой username')
    if not re.match(r'^[\w.@+-]+\Z$', username):
        raise serializers.ValidationError('Искользованы недопустипые симполы')
