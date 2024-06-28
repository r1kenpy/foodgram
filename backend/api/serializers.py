import base64

from django.core.files.base import ContentFile
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import serializers

from api.paginations import RecipesLimitPagination
from recipes.models import (
    Ingredient,
    Recipe,
    Tag,
    AmountReceptIngredients,
)
from users.models import CustomUser


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = Base64ImageField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'last_name',
            'first_name',
            'is_subscribed',
            'email',
            'avatar',
        )
        read_only_fields = (
            'id',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):

        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.subscription.filter(user=user).exists()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        fields = ('avatar',)
        model = CustomUser


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
        return obj.amount.all().aggregate(amount=Sum('amount'))['amount']


class RecipeFromFavoriteAndCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ReadRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = ReceptIngredientSerializer(many=True)
    author = CustomUserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.favorite.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.cart.filter(user=user).exists()


class WriteIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = WriteIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'text',
            'image',
            'cooking_time',
            'name',
            'ingredients',
            'author',
        )
        read_only_fields = ('id',)

        # validators = [UniqueValidator(queryset=Tag.objects.all())]

    # def validate_tags(self, tags):
    #     print(tags)
    #     pass

    # def validate_ingredients(self, ingredients):
    #     print(ingredients)
    #     pass
    #
    # def validators(self):
    #     print()

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        object_ingredients = [
            AmountReceptIngredients(
                ingredients=get_object_or_404(
                    Ingredient, id=ingredient.get('id')
                ),
                amount=ingredient.get('amount'),
                recipe=recipe,
            )
            for ingredient in ingredients
        ]
        AmountReceptIngredients.objects.bulk_create(object_ingredients)

        return recipe

    def to_representation(self, recipe):
        return ReadRecipeSerializer(
            recipe, context={'request': self.context['request']}
        ).data


class SubscribeSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )
        read_only_fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        paginator = RecipesLimitPagination()
        recipes = obj.recipe.all()
        paginator1 = paginator.paginate_queryset(
            recipes, self.context.get('request')
        )
        return RecipeFromFavoriteAndCartSerializer(paginator1, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipe.count()
