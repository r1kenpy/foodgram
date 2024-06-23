from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.paginations import CustomLimitPagination
from api.serializers import (
    AvatarSerializer,
    CustomUserSerializer,
    SubscribeSerializer,
)
from recipes.models import Subscription
from users.models import CustomUser

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Эндпоинт юзера. Позволяющий получить информацию
    об авторизованном юзере, зарегистрироваться, изменить или удалить аватар.
    """

    pagination_class = CustomLimitPagination

    @action(
        detail=False,
        methods=('GET',),
        serializer_class=CustomUserSerializer,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='subscriptions',
    )
    def user_subscriptions(self, request):
        user = request.user
        if request.method == "GET":
            subs = User.objects.get(
                username=request.user.username
            ).subscriber.all()
            serializer = CustomUserSerializer(subs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        # author = get_object_or_404(CustomUser, id=id)
        # if request.method == "POST":
        #     if author == user:
        #         return Response(
        #             {'errors': 'Нельзя подписаться на самого себя'},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     if author.subscription.filter(user=user).exists():
        #         return Response(
        #             {'errors': 'Вы уже подписаны на этого пользователя'},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     new_sub = Subscription.objects.create(
        #         user=user,
        #         author=author,
        #     )
        #     serializer = SubscribeSerializer(new_sub)
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        #
        # subscription = get_object_or_404(
        #     Subscription, user=user, author=author
        # )
        # subscription.delete()
        # return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        serializer_class=CustomUserSerializer,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request, id=None):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)
        if request.method == "POST":
            if author == user:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if author.subscription.filter(user=user).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            new_sub = Subscription.objects.create(
                user=user,
                author=author,
            )
            serializer = SubscribeSerializer(new_sub)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = get_object_or_404(
            Subscription, user=user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_user(self):
        return self.request.user

    @action(
        detail=False,
        methods=('GET',),
        serializer_class=CustomUserSerializer,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request, *args, **kwargs):
        """Получение данных об авторизованном юзере."""
        self.get_object = self.get_user
        if request.method == 'GET':
            return self.retrieve(request, *args, **kwargs)

    @action(
        detail=False,
        methods=('PUT', 'DELETE'),
        url_path='me/avatar',
        serializer_class=AvatarSerializer,
        permission_classes=(permissions.IsAuthenticated,),
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
