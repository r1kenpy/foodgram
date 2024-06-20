import base64

from django.core.files.base import ContentFile
from djoser.serializers import UsernameSerializer
from recipes.models import Ingredient, Recipe, Subscription, Tag
from rest_framework import serializers
from users.models import CustomUser


class CustomUserSerializer(UsernameSerializer):
    # is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'last_name',
            'first_name',
            # 'is_subscribed',
            'email',
        )


class SubscribedSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Subscription
        fields = (
            'id',
            'user',
        )


class SignUpSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'last_name', 'first_name', 'password')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        fields = ('avatar',)
        model = CustomUser


class AuthorSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        print(self.context)
        if obj.subscription.filter(
            user=self.context['request'].user
        ).exists():
            return True
        return False


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class ReceptIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    measurement_unit = serializers.CharField(read_only=True)
    amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AmountReceptIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, obj):
        print(obj.amount.all().aggregate(amount=Sum('amount')))
        return obj.amount.all().aggregate(amount=Sum('amount'))['amount']


class RecipeFromFavoriteAndCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ReadRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = ReceptIngredientSerializer(many=True, read_only=True)
    # author = AuthorSerializer(read_only=True)
    # is_favorited = bool
    # is_in_shopping_cart = bool

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            # is_favorited,
            # is_in_shopping_cart,
            'name',
            'image',
            'text',
            'cooking_time',
        )
