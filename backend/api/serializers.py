from django.db.models import Sum
from rest_framework import serializers

from recipes.models import Ingredient, Tag, Recipe, AmountReceptIngredients


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
