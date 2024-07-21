from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from recipes.models import Recipe
from recipes.validators import validate_link


class ShortLinkView(APIView):
    """Декодирование короткой ссылки."""

    def get(self, request, encode_id=None):
        decode_id = int(validate_link(encode_id))
        recipe = get_object_or_404(Recipe, pk=decode_id)
        return HttpResponseRedirect(
            request.build_absolute_uri(f'/recipes/{recipe.id}/')
        )
