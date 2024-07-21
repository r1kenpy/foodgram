import django_filters
from django.contrib.auth import get_user_model
from django_filters import filters
from django_filters.widgets import BooleanWidget

from recipes.models import Ingredient, Recipe

User = get_user_model()


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipesFilter(django_filters.FilterSet):
    is_favorited = django_filters.BooleanFilter(
        method='filter_recipe_is_favorited',
        label='Избранное',
        widget=BooleanWidget(),
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
        label='Корзина',
        widget=BooleanWidget(),
    )
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = django_filters.ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def filter_recipe_is_favorited(self, recipes, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return recipes.filter(favorites__user=user)
        return recipes

    def filter_is_in_shopping_cart(self, recipes, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return recipes.filter(carts__user=user)
        return recipes
