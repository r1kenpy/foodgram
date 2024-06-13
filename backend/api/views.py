from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Ingredient, Tag, Recipe, Favorite, ShoppingCart
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
    FavoriteRecipeSerializer,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientVeiwSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    @action(
        detail=True,
        methods=["POST", 'DELETE'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        if self.request.method == 'POST':
            if recipe.favorite.filter(
                author=self.request.user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этот рецепт!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Favorite.objects.create(recipe=recipe, author=self.request.user)
            serializer = FavoriteRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not recipe.favorite.filter(
            author=self.request.user, recipe=recipe
        ).exists():
            return Response(
                {'errors': 'Рецепта нет в избранном!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recipe.favorite.filter(author=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk=None):
        # add to cart
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        if self.request.method == 'POST':
            if recipe.cart.filter(author=self.request.user).exists():
                return Response(
                    'Рецепт уже есть в корзине!',
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ShoppingCart.objects.create(
                recipe=recipe, author=self.request.user
            )
            serializer = FavoriteRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # delete from cart
        if not recipe.cart.filter(author=self.request.user).exists():
            return Response(
                'Рецепта нет в корзине!', status.HTTP_400_BAD_REQUEST
            )
        recipe.cart.filter(author=self.request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'], detail=True)
    def download_shopping_cart(self):
        pass
