from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint

from .validators import validate_username


class User(AbstractUser):
    avatar = models.ImageField(
        blank=True, null=True, upload_to='users/', verbose_name='Аватар'
    )
    email = models.EmailField(
        max_length=254, unique=True, verbose_name='Email'
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    username = models.CharField(
        unique=True,
        max_length=150,
        verbose_name='Псевдоним пользователя',
        validators=[validate_username],
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


class Tag(models.Model):
    name = models.CharField(max_length=32, verbose_name='Название')
    slug = models.SlugField(
        max_length=32, verbose_name='Идентификатор', unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)
        default_related_name = 'tags'

    def __str__(self):
        return self.name[:20]


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128, verbose_name='Название', unique=True
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)
        default_related_name = 'ingredients'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


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
        Ingredient,
        through='AmountReceptIngredients',
        verbose_name='Продукты',
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.IntegerField(
        validators=[
            MinValueValidator(limit_value=settings.MIN_VALUE_COOKING_TIME)
        ],
        verbose_name='Время приготовления в минутах',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
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
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Продукт'
    )

    class Meta:
        verbose_name = 'Продукт с количеством в рецепте'
        verbose_name_plural = 'Продукты с количеством в рецепте'
        ordering = ('-amount',)
        default_related_name = 'amount_ingredients'
        constraints = [
            UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_amount_ingredient',
            )
        ]

    def __str__(self):
        return (
            f'{self.recipe.name[:20]}: {self.ingredient.name[:20]}'
            f'({self.ingredient.measurement_unit})'
        )


class BaseRecipeUser(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ('-recipe',)
        abstract = True
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='%recipes_unique',
            )
        ]

    def __str__(self):
        return (
            f'Рецепт '
            f'"{self.recipe.name[:20].title()}" '
            f' добавлен {self.user.email[:20]}'
        )


class Favorite(BaseRecipeUser):

    class Meta(BaseRecipeUser.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorites'


class ShoppingCart(BaseRecipeUser):

    class Meta(BaseRecipeUser.Meta):
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        default_related_name = 'carts'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='subscribers',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='authors',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('user',)
        constraints = [
            UniqueConstraint(
                fields=('user', 'author'), name='unique_subscription'
            ),
            CheckConstraint(
                check=~Q(author=F('user')), name='no_self_sibscription'
            ),
        ]

    def __str__(self):
        return f'{self.user.email[:20]} подписан на {self.author.email[:20]}'
