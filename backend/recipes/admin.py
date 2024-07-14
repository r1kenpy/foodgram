from django.contrib import admin
from django.contrib.admin.decorators import display
from django.contrib.auth.admin import UserAdmin
from django.db.models import Sum
from django.utils.safestring import mark_safe

from .models import (AmountReceptIngredients, Favorite, Ingredient, Recipe,
                     ShoppingCart, Subscription, Tag, User)


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


class CountRecipesFilter(admin.SimpleListFilter):
    title = 'Наличие рецептов'
    parameter_name = 'count_recipes'

    def lookups(self, request, model_admin):
        return [(1, 'Есть рецепты'), (0, 'Нет рецептов')]

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.exclude(recipes=None)
        elif self.value() == '0':
            return queryset.filter(recipes=None)


class CountSubscribersFilter(admin.SimpleListFilter):
    title = 'Наличие подписок'
    parameter_name = 'count_sub'

    def lookups(self, request, model_admin):
        return [(1, 'Есть подписки'), (0, 'Нет подписок')]

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.exclude(subscribers=None)
        elif self.value() == '0':
            return queryset.filter(subscribers=None)


class CountAuthorFilter(admin.SimpleListFilter):
    title = 'Наличие подписчиков'
    parameter_name = 'count_author'

    def lookups(self, request, model_admin):
        return [(1, 'Есть подписчики'), (0, 'Нет подписчики')]

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.exclude(authors=None)
        elif self.value() == '0':
            return queryset.filter(authors=None)


@admin.register(User)
class UserAdmin(UserAdmin):
    search_fields = ['username', 'email']

    list_display = UserAdmin.list_display + (
        'count_recipes',
        'count_subscribers',
        'count_author',
    )
    list_filter = UserAdmin.list_filter + (
        CountRecipesFilter,
        CountSubscribersFilter,
        CountAuthorFilter,
    )

    @display(description='Количество рецептов')
    def count_recipes(self, user):
        return user.recipes.count()

    @display(description='Количество подписок')
    def count_subscribers(self, user):
        return user.subscribers.count()

    @display(description='Количество подписчиков')
    def count_author(self, user):
        return user.authors.count()


admin.site.register(
    (
        AmountReceptIngredients,
        Subscription,
    )
)
