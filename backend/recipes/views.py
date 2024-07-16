import re

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.views import APIView

from recipes.models import Recipe


class ShortLinkView(APIView):
    """Декодирование короткой ссылки."""

    def get(self, request, encode_id=None):

        if re.match(r'\b0', encode_id):
            raise serializers.ValidationError(
                {'errors': 'Рецепт не может начинатся с 0'}
            )
        invalid_simbol = re.findall(r'[\D]', encode_id)
        if invalid_simbol:
            raise serializers.ValidationError(
                {'errors': f'Запрещенный символ в ссылке: {invalid_simbol}.'}
            )

        decode_id = int(encode_id)
        recipe = get_object_or_404(Recipe, pk=decode_id)
        return HttpResponseRedirect(
            request.build_absolute_uri(f'/recipes/{recipe.id}/')
        )
