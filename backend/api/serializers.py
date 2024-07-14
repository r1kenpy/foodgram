from django.db.models import Sum
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (AmountReceptIngredients, Ingredient, Recipe, Tag,
                            User)


def check_duplicates(ids: list, msg='errors'):
    no_duplicate_ingredients = set(ids)
    if len(ids) != len(no_duplicate_ingredients):
        duplicate = set(
            id for id in no_duplicate_ingredients if ids.count(id) > 1
        )
        raise serializers.ValidationError(
            {msg: f'Переданы одинаковые id: {duplicate}'}
        )


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = Base64ImageField(read_only=True)
    username = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + (
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, author):

        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return author.authors.filter(user=user).exists()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        fields = ('avatar',)
        model = User


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
        return obj.amount_ingredients.all().aggregate(amount=Sum('amount'))[
            'amount'
        ]


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ReadRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = ReceptIngredientSerializer(many=True)
    author = UserSerializer()
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
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.carts.filter(user=user).exists()


class WriteIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = WriteIngredientSerializer(
        many=True,
    )
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

    def validate(self, attrs):
        ingredients = attrs.get('ingredients')
        tags = attrs.get('tags')
        if ingredients is None or len(ingredients) == 0:
            raise serializers.ValidationError(
                {'ingredients': 'Необходимо минимум 1 ингредиент'}
            )
        ingredients_id = [ingredient['id'] for ingredient in ingredients]
        check_duplicates(ids=ingredients_id, msg='ingredients')
        amount_less_zero = []
        for ingredient in ingredients:
            if ingredient['amount'] < 1:
                amount_less_zero.append(
                    {'id': ingredient['id'], 'amount': ingredient['amount']}
                )
        if amount_less_zero:
            raise serializers.ValidationError(
                {
                    'amount': (
                        'Количество ингредиентов не может быть меньше 1: '
                        f'{amount_less_zero}'
                    )
                }
            )
        if tags is None or len(tags) == 0:
            raise serializers.ValidationError(
                {'tags': 'Нужно передать хоть один Тег'}
            )
        tags_id = [tag.id for tag in tags]
        check_duplicates(ids=tags_id, msg='tags')
        return attrs

    def add_ingredients_in_recipe(self, ingredients, recipe):
        AmountReceptIngredients.objects.bulk_create(
            [
                AmountReceptIngredients(
                    ingredients=get_object_or_404(
                        Ingredient, id=ingredient.get('id')
                    ),
                    amount=ingredient.get('amount'),
                    recipe=recipe,
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_ingredients_in_recipe(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        recipe.ingredients.clear()
        recipe.tags.set(tags)
        self.add_ingredients_in_recipe(ingredients, recipe)
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        return ReadRecipeSerializer(
            recipe, context={'request': self.context['request']}
        ).data


class SubscribeSerializer(UserSerializer):
    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )
        read_only_fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )
