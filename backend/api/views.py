import io

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.baseconv import BASE64_ALPHABET, base64
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from api.filters import IngredientFilter, RecipesFilter
from api.paginations import LimitSizePagination
from api.permissions import ReadOrIsAuthenticatedPermission
from api.serializers import (
    IngredientSerializer,
    ReadRecipeSerializer,
    RecipeFromFavoriteAndCartSerializer,
    RecipeSerializer,
    TagSerializer,
)
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение информации о тегах."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientVeiwSet(viewsets.ReadOnlyModelViewSet):
    """Получение информации об ингридиентах.
    Возможен поиск по имени рецепту."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Получение, изменение или удаление рецепта.
    Так же сюда относится корзина, избранное и скачивание файла.
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
        """Создание короткой ссылки."""
        recipe = self.get_object()
        base = base64.encode(recipe.id)
        url = request.build_absolute_uri(
            reverse('recipes:shortlink', args=(base,))
        )
        return Response({'short-link': url}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """Добавление или удаление рецепта из избранного."""
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        if self.request.method == 'POST':
            if recipe.favorites.filter(
                user=self.request.user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранном!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Favorite.objects.create(recipe=recipe, user=self.request.user)
            serializer = RecipeFromFavoriteAndCartSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not recipe.favorites.filter(
            user=self.request.user, recipe=recipe
        ).exists():
            return Response(
                {'errors': 'Рецепта нет в избранном!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recipe.favorites.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('POST', 'DELETE'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Добавление или удаление рецепта из корзины."""
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        if self.request.method == 'POST':
            if recipe.carts.filter(user=self.request.user).exists():
                return Response(
                    'Рецепт уже есть в корзине!',
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ShoppingCart.objects.create(recipe=recipe, user=self.request.user)
            serializer = RecipeFromFavoriteAndCartSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not recipe.carts.filter(user=self.request.user).exists():
            return Response(
                {'errors': 'Рецепта нет в корзине!'},
                status.HTTP_400_BAD_REQUEST,
            )
        recipe.carts.filter(user=self.request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('GET',),
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Скачивание файла со списком и количеством ингредиентов."""
        shopping_cart = ShoppingCart.objects.prefetch_related('recipe').filter(
            user=request.user
        )
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
        text = c.beginText()
        text.setTextOrigin(20, 20)
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        text.setFont('DejaVuSans', 14)
        if shopping_cart:
            text.textLine('Shopping list:')
            for shopping_cart_item in shopping_cart:
                ingredients = [
                    (
                        f'{ingred.name}({ingred.measurement_unit}): '
                        f'{ingred.amount.aggregate(sum=Sum("amount"))["sum"]}'
                    )
                    for ingred in set(
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
    """Декодирование короткой ссылки."""

    def get(self, request, encode_id=None):
        if not set(encode_id).issubset(set(BASE64_ALPHABET)):
            return Response({'errors': 'Запрещенный символ в ссылке.'})
        decode_id = base64.decode(encode_id)
        recipe = get_object_or_404(Recipe, pk=decode_id)
        return HttpResponseRedirect(
            request.build_absolute_uri(f'/recipes/{recipe.id}/')
        )


from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.paginations import LimitSizePagination
from api.serializers import (
    AvatarSerializer,
    SubscribeSerializer,
)
from recipes.models import Subscription

User = get_user_model()


class UserViewSet(UserViewSet):
    '''Эндпоинт юзера. Позволяющий получить информацию
    об авторизованном юзере, зарегистрироваться, изменить или удалить аватар.
    '''

    pagination_class = LimitSizePagination

    @action(
        ('get',),
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        detail=False,
        methods=('GET',),
        serializer_class=SubscribeSerializer,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        user = request.user
        subs = User.objects.filter(subscription__user=user)
        page = self.paginate_queryset(subs)
        serializer = self.serializer_class(page, many=True)
        serializer.context['request'] = self.request
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        serializer_class=SubscribeSerializer,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = self.get_object()
        if request.method == 'POST':
            if author == user:
                raise ValidationError(
                    {'errors': 'Нельзя подписаться на самого себя'}
                )
            if author.author.filter(user=user).exists():
                raise ValidationError(
                    {'errors': 'Вы уже подписаны на этого пользователя'}
                )
            Subscription.objects.create(
                user=user,
                author=author,
            )
            serializer = self.serializer_class(author)
            serializer.context['request'] = self.request
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(Subscription, author=author, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        # return Response(
        #     {'errors': 'Вы не подписаны на данного пользователя!'},
        #     status=status.HTTP_400_BAD_REQUEST,
        # )

    @action(
        detail=False,
        methods=('PUT', 'DELETE'),
        url_path='me/avatar',
        serializer_class=AvatarSerializer,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def avatar(self, request, *args, **kwargs):
        '''Изменение или удаление аватара.'''
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'DELETE' and user.avatar:
            user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
