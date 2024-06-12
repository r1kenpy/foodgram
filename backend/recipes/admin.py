from django.contrib import admin

from .models import Ingredient, Recipe, Tag, Favorite

admin.site.register((Ingredient, Recipe, Tag, Favorite))
