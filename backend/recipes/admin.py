from django.contrib import admin
from django.contrib.admin.decorators import display
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
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


@admin.register(AmountReceptIngredients)
class AmountReceptIngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient',
        'recipe',
        'amount',
        'measurement_unit',
    )
    readonly_fields = ('measurement_unit',)

    @display(description='Единица измерения')
    def measurement_unit(self, amount_ingredients):
        return amount_ingredients.ingredient.measurement_unit


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

    @display(description='Рецепты')
    def number_of_recipes(self, tag):
        return tag.recipes.count()


class RecipeInline(admin.StackedInline):
    model = AmountReceptIngredients
    extra = 0
    fieldsets = [
        (
            None,
            {
                'fields': [('ingredient', 'amount', 'measurement_unit')],
            },
        ),
    ]
    readonly_fields = ('measurement_unit',)

    @display(description='Единица измерения')
    def measurement_unit(self, recipe):
        return recipe.ingredient.measurement_unit


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
    list_filter = ('tags', 'author')
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
        return f'<img src="{recipe.image.url}" width="100px">'

    @display(description='Теги')
    def get_tags(self, recipe):
        return list(recipe.tags.all())

    @display(description='Продукты')
    @mark_safe
    def get_ingredients(self, recipe):
        return '<br>'.join(
            [
                f'{recipe_ingredient.ingredient.name.title()}: '
                f'{recipe_ingredient.amount}'
                f'({recipe_ingredient.ingredient.measurement_unit})'
                for recipe_ingredient in recipe.amount_ingredients.all()
            ]
        )

    @display(description='Избранное')
    def favorites(self, recipe):
        return recipe.favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'amount',
        'measurement_unit',
        'recipe',
    )
    search_fields = ('name', 'measurement_unit')
    list_filter = ('recipes__name', 'measurement_unit')

    @display(description='Количество')
    def amount(self, ingredient):
        return ingredient.amount_ingredients.aggregate(sum=Sum('amount')).get(
            'sum'
        )

    @display(description='Рецепты')
    def recipe(self, ingredient):
        return ingredient.recipes.count()


@admin.register(User)
class UserAdmin(UserAdmin):
    search_fields = ['username', 'email']

    list_display = (
        *UserAdmin.list_display,
        'count_recipes',
        'count_subscribers',
        'count_author',
    )
    list_filter = (
        *UserAdmin.list_filter,
        'recipes__name',
        'subscribers__user',
        'authors__author',
    )

    @display(description='Рецептов')
    def count_recipes(self, user):
        return user.recipes.count()

    @display(description='Подписок')
    def count_subscribers(self, user):
        return user.subscribers.count()

    @display(description='Подписчиков')
    def count_author(self, user):
        return user.authors.count()


admin.site.register((Subscription,))


admin.site.unregister(Group)
