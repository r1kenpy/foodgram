from django.contrib import admin

from .models import (
    AmountReceptIngredients,
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
    Subscription,
)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')


admin.site.register(
    (
        Ingredient,
        Recipe,
        Tag,
        AmountReceptIngredients,
        Subscription,
    )
)
