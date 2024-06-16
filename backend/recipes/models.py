from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=32, verbose_name=_('Название'))
    slug = models.SlugField(max_length=32, verbose_name=_('Слаг'), unique=True)

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')
        ordering = ('name',)
        default_related_name = 'tag'

    def __str__(self) -> str:
        return self.name[:20]


class Ingredient(models.Model):
    name = models.CharField(max_length=128, verbose_name=_('Название'))
    measurement_unit = models.CharField(
        max_length=64, verbose_name=_('Единица измерения')
    )

    class Meta:
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        ordering = ('name',)
        default_related_name = 'ingredient'

    def __str__(self) -> str:
        return self.name[:20]


class Recipe(models.Model):
    author = models.ForeignKey(
        User, verbose_name=_('Автор'), on_delete=models.CASCADE
    )
    name = models.CharField(max_length=256, verbose_name=_('Название'))
    text = models.TextField(verbose_name=_('Описание'))
    image = models.ImageField(
        verbose_name=_('Картинка'), upload_to='recipe/images/'
    )
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name=_('Ингредиенты')
    )
    tags = models.ManyToManyField(Tag, verbose_name=_('Теги'))
    cooking_time = models.IntegerField(verbose_name=_('Время приготовления'))

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')
        ordering = ('name',)
        default_related_name = 'recipe'

    def __str__(self) -> str:
        return self.name[:20]


class Favorite(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_('Автор')
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name=_('Рецепт')
    )

    class Meta:
        verbose_name = _('Избранное')
        verbose_name_plural = _('Избранное')
        ordering = ('-recipe',)
        default_related_name = 'favorite'


class ShoppingCart(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Корзина')
        verbose_name_plural = _('Корзина')
        ordering = ('-recipe',)
        default_related_name = 'cart'
