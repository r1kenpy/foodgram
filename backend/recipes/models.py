from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=32, verbose_name='Название')
    slug = models.SlugField(max_length=32, verbose_name='Слаг', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)
        default_related_name = 'tag'

    def __str__(self) -> str:
        return self.name[:20]


class Ingredient(models.Model):
    name = models.CharField(max_length=128, verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=64, verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        default_related_name = 'ingredient'

    def __str__(self) -> str:
        return self.name[:20]


class Recipe(models.Model):
    author = models.ForeignKey(
        User, verbose_name='Автор', on_delete=models.CASCADE
    )
    name = models.CharField(max_length=256, verbose_name='Название')
    text = models.TextField(verbose_name='Описание')
    image = models.ImageField(
        verbose_name='Картинка', upload_to='recipe/images/'
    )
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.IntegerField(verbose_name='Время приготовления')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)
        default_related_name = 'recipe'

    def __str__(self) -> str:
        return self.name[:20]


class Favorite(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('-recipe',)
        default_related_name = 'favorite'


class ShoppingCart(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        ordering = ('-recipe',)
        default_related_name = 'cart'
