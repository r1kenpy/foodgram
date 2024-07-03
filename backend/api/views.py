import io

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.baseconv import base64, BASE64_ALPHABET
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import (
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)
from .filters import RecipesFilter, IngredientFilter
from .paginations import LimitSizePagination
from .permissions import ReadOrIsAuthenticatedPermission
from .serializers import (
    IngredientSerializer,
    RecipeFromFavoriteAndCartSerializer,
    TagSerializer,
    ReadRecipeSerializer,
    RecipeSerializer,
)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientVeiwSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Получение, изменение или удаление рецепта.
    Так же сюда относится корзина, избранное и скачивание файлов.
    """

    queryset = Recipe.objects.all()
    pagination_class = LimitSizePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    permission_classes = (ReadOrIsAuthenticatedPermission,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadRecipeSerializer
        return RecipeSerializer

    @action(methods=['GET'], detail=True, url_path='get-link')
    def getlink(self, request, pk=None):
        recipe = self.get_object()
        base = base64.encode(recipe.id)
        encode_id = request.build_absolute_uri(
            reverse('shortlink', args=(base,))
        )
        return Response({'short-link': encode_id}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """Добавление или удаление рецепта из избранного."""
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        if self.request.method == 'POST':
            if recipe.favorite.filter(
                user=self.request.user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранном!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Favorite.objects.create(recipe=recipe, user=self.request.user)
            serializer = RecipeFromFavoriteAndCartSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not recipe.favorite.filter(
            user=self.request.user, recipe=recipe
        ).exists():
            return Response(
                {'errors': 'Рецепта нет в избранном!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recipe.favorite.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('POST', 'DELETE'), detail=True)
    def shopping_cart(self, request, pk=None):
        """Добавление или удаление рецепта из корзины."""
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        if self.request.method == 'POST':
            if recipe.cart.filter(user=self.request.user).exists():
                return Response(
                    'Рецепт уже есть в корзине!',
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ShoppingCart.objects.create(recipe=recipe, user=self.request.user)
            serializer = RecipeFromFavoriteAndCartSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not recipe.cart.filter(user=self.request.user).exists():
            return Response(
                {'errors': 'Рецепта нет в корзине!'},
                status.HTTP_400_BAD_REQUEST,
            )
        recipe.cart.filter(user=self.request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('GET',), detail=False)
    def download_shopping_cart(self, request):
        """Скачивание файла со списком и количеством ингредиентов."""
        shopping_cart = ShoppingCart.objects.prefetch_related('recipe').filter(
            user=self.request.user
        )
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
        text = c.beginText()
        text.setTextOrigin(20, 20)
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        text.setFont('Arial', 14)
        if shopping_cart:
            text.textLine('Shopping list:')
            for shopping_cart_item in shopping_cart:
                ingredients = [
                    f'{ingredient.name}({ingredient.measurement_unit}): {ingredient.amount.aggregate(Sum("amount")).get("amount__sum")}'
                    for ingredient in set(
                        shopping_cart_item.recipe.ingredients.all()
                    )
                ]
            text.textLines(ingredients)
        else:
            text.textLine('Shopping list is empty!')
        c.drawText(text)
        c.showPage()
        c.save()
        buf.seek(0)

        return FileResponse(
            buf,
            filename=f'shopping_list_{timezone.now().date()}.pdf',
        )


class ShortLinkView(APIView):

    def get(self, request, encode_id=None):
        if not set(encode_id).issubset(set(BASE64_ALPHABET)):
            return Response({'errors': 'Запрещенный символ в ссылке.'})
        decode_id = base64.decode(encode_id)
        recipe = get_object_or_404(Recipe, pk=decode_id)
        return HttpResponseRedirect(
            request.build_absolute_uri(f'/api/recipes/{recipe.id}/')
        )
