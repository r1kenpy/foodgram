from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Sum

from .models import (
    AmountReceptIngredients,
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
    User,
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


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')


class RecipeInline(admin.StackedInline):
    model = Recipe.ingredients.through
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeInline,)
    list_display = ('name', 'author', 'favorites')
    list_filter = ('tags',)
    search_fields = ('name', 'author')

    def favorites(self, obj):
        return obj.favorite.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount')
    search_fields = ('name',)

    def amount(self, obj):
        amount = obj.amount
        if amount.exists():
            return amount.aggregate(sum=Sum('amount')).get('sum')


@admin.register(User)
class UserAdmin(UserAdmin):
    search_fields = ['username', 'email']


admin.site.register(
    (
        AmountReceptIngredients,
        Subscription,
    )
)
