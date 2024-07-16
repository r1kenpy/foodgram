from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint, F, CheckConstraint, Q
from django.utils.translation import gettext_lazy as _

from .validators import validate_username


class User(AbstractUser):
    avatar = models.ImageField(
        blank=True, null=True, upload_to='users/', verbose_name=_('Аватар')
    )
    email = models.EmailField(
        max_length=254, unique=True, verbose_name=_('Email')
    )
    first_name = models.CharField(_('Имя'), max_length=150)
    last_name = models.CharField(_('Фамилия'), max_length=150)
    username = models.CharField(
        unique=True,
        max_length=150,
        verbose_name=_('Псевдоним пользователя'),
        validators=[validate_username],
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ('username',)


class Tag(models.Model):
    name = models.CharField(max_length=32, verbose_name=_('Название'))
    slug = models.SlugField(
        max_length=32, verbose_name=_('Идентификатор'), unique=True
    )

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')
        ordering = ('name',)
        default_related_name = 'tags'

    def __str__(self):
        return self.name[:20]


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128, verbose_name=_('Название'), unique=True
    )
    measurement_unit = models.CharField(
        max_length=64, verbose_name=_('Единица измерения')
    )

    class Meta:
        verbose_name = _('Продукт')
        verbose_name_plural = _('Продукты')
        ordering = ('name',)
        default_related_name = 'ingredients'

    def __str__(self):
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
        Ingredient,
        through='AmountReceptIngredients',
        verbose_name=_('Продукты'),
    )
    tags = models.ManyToManyField(Tag, verbose_name=_('Теги'))
    cooking_time = models.IntegerField(
        validators=[
            MinValueValidator(limit_value=settings.MIN_VALUE_COOKING_TIME)
        ],
        verbose_name=_('Время приготовления в минутах'),
    )

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')
        ordering = ('name',)
        default_related_name = 'recipes'

    def __str__(self):
        return self.name[:20]


class AmountReceptIngredients(models.Model):
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(limit_value=settings.MIN_VALUE_AMOUNT)],
        verbose_name='Мера',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name=_('Рецепт')
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name=_('Ингредиент')
    )

    class Meta:
        verbose_name = _('Мера')
        verbose_name_plural = _('Мера')
        ordering = ('-amount',)
        default_related_name = 'amount_ingredients'

    def __str__(self):
        return f'{self.recipe.name[:20]}: {self.ingredient[:20]}'


class FavoriteAndCartBaseModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт'),
    )

    class Meta:
        ordering = ('-recipe',)
        abstract = True


class Favorite(FavoriteAndCartBaseModel):

    class Meta(FavoriteAndCartBaseModel.Meta):
        verbose_name = _('Избранное')
        verbose_name_plural = _('Избранное')
        default_related_name = 'favorites'
        abstract = False
        constraints = [
            UniqueConstraint(fields=('user', 'recipe'), name='unique_favorite')
        ]

    def __str__(self):
        return (
            f'Рецепт '
            f'"{self.recipe.name[:20].title()}" '
            f'в избранном у {self.user.email[:20]}'
        )


class ShoppingCart(FavoriteAndCartBaseModel):

    class Meta(FavoriteAndCartBaseModel.Meta):
        verbose_name = _('Корзина')
        verbose_name_plural = _('Корзина')
        default_related_name = 'carts'
        abstract = False
        constraints = [
            UniqueConstraint(fields=('user', 'recipe'), name='unique_cart')
        ]

    def __str__(self):
        return (
            f'Рецепт '
            f'"{self.recipe.name[:20].title()}" '
            f'в корзине у {self.user.email[:20]}'
        )


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Подписчик'),
        related_name='subscribers',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Автор рецепта'),
        related_name='authors',
    )

    class Meta:
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
        ordering = ('user',)
        constraints = [
            UniqueConstraint(
                fields=('user', 'author'), name='unique_subscription'
            ),
            CheckConstraint(
                check=~Q(author=F("user")), name="\nNo self sibscription\n"
            ),
        ]

    def __str__(self):
        return f'{self.user.email[:20]} подписан на {self.author.email[:20]}'
