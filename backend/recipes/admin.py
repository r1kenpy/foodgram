from django.contrib import admin

from .models import (
    AmountReceptIngredients,
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'recipe')
    list_filter = ('author', 'recipe')
    search_fields = ('author', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'recipe')
    list_filter = ('author', 'recipe')
    search_fields = ('author', 'recipe')


admin.site.register(
    (
        Ingredient,
        Recipe,
        Tag,
        AmountReceptIngredients,
        Subscription,
    )
)
