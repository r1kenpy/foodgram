from django.contrib import admin
from django.contrib.admin.decorators import display
from django.contrib.auth.admin import UserAdmin
from django.db.models import Sum
from django.utils.safestring import mark_safe

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
    list_display = ('id', 'name', 'slug', 'number_of_recipes')
    search_fields = ('name', 'slug')

    def number_of_recipes(self, obj):
        return obj.recipes.count()


class RecipeInline(admin.StackedInline):
    model = Recipe.ingredients.through
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeInline,)
    list_display = (
        'name',
        'author',
        'favorites',
        'cooking_time',
        'get_ingredients',
        'get_tags',
        'get_html_image',
    )
    list_filter = ('tags',)
    search_fields = (
        'name',
        'author__first_name',
        'author__username',
        'author__email',
        'tags__name',
    )

    @display(description='Картинка')
    @mark_safe
    def get_html_image(self, recipe):
        if recipe.image:
            return f'<img src="{recipe.image.url}" width="100px">'

    @display(description='Теги')
    def get_tags(self, recipe):
        return list(recipe.tags.all())

    @display(description='Продукты')
    def get_ingredients(self, recipe):
        return list(recipe.ingredients.all())

    def favorites(self, recipe):
        return recipe.favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount')
    search_fields = ('name',)

    def amount(self, obj):
        amount = obj.amount_ingredients
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
