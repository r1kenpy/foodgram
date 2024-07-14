from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipesFilter
from api.paginations import RecipesLimitPagination
from api.permissions import ReadOrAuthorChangeRecipt
from api.serializers import (AvatarSerializer, IngredientSerializer,
                             ReadRecipeSerializer, RecipeSerializer,
                             ShortRecipeSerializer, SubscribeSerializer,
                             TagSerializer, UserSerializer)
from api.utils import create_pdf_shopping_list
from recipes.models import (Favorite, Ingredient, Recipe, ShoppingCart,
                            Subscription, Tag)

User = get_user_model()


def add_favorite_or_cart(self, request, model, pk=None):
    recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
    if self.request.method == 'POST':
        model.objects.create(user=request.user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    get_object_or_404(model, user=self.request.user, recipe=recipe).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение информации о тегах."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientVeiwSet(viewsets.ReadOnlyModelViewSet):
    """Получение информации об ингридиентах.
    Возможен поиск по имени рецепту."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Получение, изменение или удаление рецепта.
    Так же сюда относится корзина, избранное и скачивание файла.
    """

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        ReadOrAuthorChangeRecipt,
    )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadRecipeSerializer
        return RecipeSerializer

    @action(methods=['GET'], detail=True, url_path='get-link')
    def getlink(self, request, pk=None):
        """Создание короткой ссылки."""
        recipe = self.get_object()
        id = str(recipe.id)
        url = request.build_absolute_uri(
            reverse('recipes:shortlink', args=(id,))
        )
        return Response({'short-link': url}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """Добавление или удаление рецепта из избранного."""
        return add_favorite_or_cart(
            self,
            request,
            model=Favorite,
            pk=pk,
        )

    @action(
        methods=('POST', 'DELETE'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Добавление или удаление рецепта из корзины."""
        return add_favorite_or_cart(
            self,
            request,
            model=ShoppingCart,
            pk=pk,
        )

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
        ingredients = []
        recipe_in_shopping_cart = []
        numbering = 1
        if shopping_cart:
            for shopping_cart_item in shopping_cart:
                recipe_in_shopping_cart.append(
                    f'"{shopping_cart_item.recipe.name}"'
                )
                for ing in set(shopping_cart_item.recipe.ingredients.all()):
                    ingredients.append(
                        (
                            f'{numbering}. {str(ing.name).capitalize()}('
                            f'{ing.measurement_unit}): '
                            f'{ing.amo.aggregate(sum=Sum("amount"))["sum"]}'
                        )
                    )
                    numbering += 1
        buf = create_pdf_shopping_list(ingredients, recipe_in_shopping_cart)
        return FileResponse(
            buf,
            filename='shopping_list.pdf',
        )


class UserViewSet(UserViewSet):
    '''Эндпоинт юзера. Позволяющий получить информацию
    об авторизованном юзере, зарегистрироваться, изменить или удалить аватар.
    '''

    serializer_class = UserSerializer

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
        paginator = RecipesLimitPagination()
        page = paginator.paginate_queryset(
            User.objects.filter(authors__user=request.user), request
        )
        serializer = self.serializer_class(page, many=True)
        serializer.context['request'] = self.request
        return paginator.get_paginated_response(serializer.data)

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
            Subscription.objects.create(
                user=user,
                author=author,
            )
            serializer = self.serializer_class(author)
            serializer.context['request'] = self.request
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(Subscription, author=author, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
