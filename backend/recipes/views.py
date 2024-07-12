from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.baseconv import BASE64_ALPHABET
from rest_framework import serializers
from rest_framework.views import APIView

from recipes.models import Recipe


class ShortLinkView(APIView):
    """Декодирование короткой ссылки."""

    def get(self, request, encode_id=None):
        if not set(encode_id).issubset(set(BASE64_ALPHABET)):
            raise serializers.ValidationError(
                {'errors': 'Запрещенный символ в ссылке.'}
            )
        decode_id = int(encode_id)
        recipe = get_object_or_404(Recipe, pk=decode_id)
        return HttpResponseRedirect(
            request.build_absolute_uri(f'/recipes/{recipe.id}/')
        )
