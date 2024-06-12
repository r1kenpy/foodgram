from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from recipes.models import Ingredient, Tag, Recipe, Favorite
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    FavoriteSerializer,
    RecipeSerializer,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientVeiwSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class FavoriteViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    serializer_class = FavoriteSerializer

    def get_recipe(self):
        return get_object_or_404(Recipe, pk=self.kwargs['id'])

    def get_queryset(self):
        return self.get_recipe().favorite.get(author=self.request.user)

    def create(self, request, *args, **kwargs):
        recipe = self.get_recipe()
        if Favorite.objects.filter(recipe=recipe.id).exists():
            return Response(
                {'errors': 'Вы уже подписаны на этот рецепт!'},
                status=400,
            )
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, recipe=self.get_recipe())


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
