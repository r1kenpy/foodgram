import io

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rest_framework import viewsets, status, permissions, pagination
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
    pagination_class = pagination.PageNumberPagination

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

    @action(methods=['GET'], detail=False)
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.prefetch_related('recipe').filter(
            author=self.request.user
        )
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
        text = c.beginText()
        text.setTextOrigin(20, 20)
        text.setFont('Helvetica', 14)
        text.textLine('Shopping list:')
        for shopping_cart_item in shopping_cart:
            ingredients = [
                f'{ingredient.name}({ingredient.measurement_unit}): {ingredient.value}'
                for ingredient in shopping_cart_item.recipe.ingredients.all()
            ]

        text.textLines(ingredients)
        c.drawText(text)

        c.showPage()
        c.save()
        buf.seek(0)
        return FileResponse(
            buf,
            as_attachment=True,
            filename=f'shopping_list_{timezone.now().date()}.pdf',
        )
