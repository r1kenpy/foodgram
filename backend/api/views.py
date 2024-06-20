import io

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from djoser.views import UserViewSet
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rest_framework import viewsets, status, permissions, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    Favorite,
    ShoppingCart,
    Subscription,
)
from users.models import CustomUser
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
    RecipeFromFavoriteAndCartSerializer,
    AvatarSerializer,
    CustomUserSerializer,
    AuthorSerializer,
    SubscribedSerializer,
)


class UserSignInAPIView(APIView):
    """Получение токена авторизации."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        user = get_object_or_404(
            CustomUser,
            email=request.data.get('email', ''),
            password=request.data.get('password', ''),
        )
        # serializer = SignUpSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        return Response(
            {'token': str((AccessToken.for_user(user)))},
            status=status.HTTP_200_OK,
        )


class CustomUserViewSet(UserViewSet):
    """Эндпоинт юзера. Позволяющий получить информацию
    об авторизованном юзере, зарегистрироваться, изменить или удалить аватар.
    """

    serializer_class = CustomUserSerializer

    @action(
        detail=False,
        methods=["GET"],
        serializer_class=AuthorSerializer,
        permission_classes=[permissions.AllowAny],
    )
    def subscriptions(self, request, *args, **kwargs):
        my = Subscription.objects.filter(user=request.user)
        serializer = SubscribedSerializer(my, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # queryset = CustomUser.objects.all()
    # pagination_class = pagination.PageNumberPagination
    #
    def get_user(self):
        return self.request.user

    #
    # def get_serializer_class(self):
    #     if self.request.method == 'POST':
    #         return SignUpSerializer
    #     return AuthorSerializer
    #
    # # .
    # def post(self, request, *args, **kwargs):
    #     """Регистрация пользователя."""
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    #
    @action(
        detail=False,
        methods=['GET'],
        serializer_class=AuthorSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        """Получение данных об авторизованном юзере."""
        self.get_object = self.get_user
        if request.method == 'GET':
            return self.retrieve(request, *args, **kwargs)

    @action(
        detail=False,
        methods=['PUT', 'DELETE'],
        url_path='me/avatar',
        serializer_class=AvatarSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def avatar(self, request, *args, **kwargs):
        """Изменение или удаление аватара."""
        user = self.get_user()
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


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientVeiwSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Получение, изменение или удаление рецепта.
    Так же сюда относится корзина, избранное и скачивание файлов.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = pagination.PageNumberPagination

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        """Добавление или удаление рецепта из избранного"""
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
            serializer = RecipeFromFavoriteAndCartSerializer(recipe)
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
        """Добавление или удаление рецепта из корзины."""
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
            serializer = RecipeFromFavoriteAndCartSerializer(recipe)
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
        """Скачивание файла со списком и количеством ингредиентов."""
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
