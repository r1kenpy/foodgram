import base64

from django.core.files.base import ContentFile
from django.db.models import F
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

from recipes.models import (AmountReceptIngredients, Ingredient, Recipe, Tag,
                            User)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


def minimal_amount_tags_or_ingredients_and_check_duplicates(
    objects, ids: list, validated_field=''
):
    if objects is None or len(objects) == 0:
        raise serializers.ValidationError(
            {validated_field: 'Нужно передать хотя бы 1.'}
        )

    no_duplicate = set(ids)
    duplicates = set(id for id in no_duplicate if ids.count(id) > 1)
    if duplicates:
        raise serializers.ValidationError(
            {validated_field: f'Переданы одинаковые id: {duplicates}'}
        )


class UserSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = Base64ImageField(read_only=True)

    class Meta:
        model = User
        fields = (
            *BaseUserSerializer.Meta.fields,
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
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, ingredient):
        return (
            ingredient.amount_ingredients.filter(
                recipe=self.context['request']
                .parser_context.get('kwargs')
                .get('pk')
            )
            .values()[0]
            .get('amount')
        )


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ReadRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
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

    def get_ingredients(self, recipe):
        return recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('amount_ingredients__amount'),
        )

    def get_is_favorited(self, recipe):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return recipe.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return recipe.carts.filter(user=user).exists()


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
    image = Base64ImageField(required=True)

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

        minimal_amount_tags_or_ingredients_and_check_duplicates(
            objects=ingredients,
            ids=[ingredient['id'] for ingredient in ingredients],
            validated_field='ingredients',
        )

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
                        'Количество продуктов не может быть меньше 1: '
                        f'{amount_less_zero}'
                    )
                }
            )
        minimal_amount_tags_or_ingredients_and_check_duplicates(
            objects=tags,
            ids=[tag.id for tag in tags],
            validated_field='tags',
        )
        return attrs

    def add_ingredients_in_recipe(self, ingredients, recipe):
        AmountReceptIngredients.objects.bulk_create(
            AmountReceptIngredients(
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
                recipe=recipe,
            )
            for ingredient in ingredients
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
        return ReadRecipeSerializer(recipe, context=self.context).data


class SubscribeSerializer(UserSerializer):
    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )

    class Meta(UserSerializer.Meta):
        fields = (
            *UserSerializer.Meta.fields,
            'recipes',
            'recipes_count',
        )
        read_only_fields = fields
