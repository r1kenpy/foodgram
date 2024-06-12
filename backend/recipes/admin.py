from django.contrib import admin

from .models import Ingredient, Recipe, Tag, Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'recipe')
    list_filter = ('author', 'recipe')


admin.site.register((Ingredient, Recipe, Tag))
