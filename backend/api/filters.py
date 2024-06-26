import django_filters
from django_filters.widgets import BooleanWidget

from recipes.models import Recipe


class RecipesFilter(django_filters.FilterSet):
    is_favorited = django_filters.BooleanFilter(
        method='filter_is_favorited', label='Избранное', widget=BooleanWidget()
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
        label='Корзина',
        widget=BooleanWidget(),
    )
    tags = django_filters.CharFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author__id',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(cart__user=user)
        return queryset
