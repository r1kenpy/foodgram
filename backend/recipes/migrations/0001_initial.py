# Generated by Django 3.2.3 on 2024-06-12 12:50

import django.core.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Избранное',
                'verbose_name_plural': 'Избранное',
                'ordering': ('-recipe',),
                'default_related_name': 'favorite',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'name',
                    models.CharField(max_length=128, verbose_name='Название'),
                ),
                (
                    'measurement_unit',
                    models.CharField(
                        max_length=64, verbose_name='Единица измерения'
                    ),
                ),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ('name',),
                'default_related_name': 'ingredient',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'name',
                    models.CharField(max_length=256, verbose_name='Название'),
                ),
                ('text', models.TextField(verbose_name='Описание')),
                (
                    'image',
                    models.ImageField(
                        upload_to='recipe/images/', verbose_name='Картинка'
                    ),
                ),
                (
                    'cooking_time',
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                limit_value=1
                            )
                        ],
                        verbose_name='Время приготовления',
                    ),
                ),
                (
                    'author',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='recipe',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Автор',
                    ),
                ),
                (
                    'ingredients',
                    models.ManyToManyField(
                        related_name='recipe',
                        to='recipes.Ingredient',
                        verbose_name='Ингредиенты',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('name',),
                'default_related_name': 'recipe',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'name',
                    models.CharField(max_length=32, verbose_name='Название'),
                ),
                (
                    'slug',
                    models.SlugField(
                        max_length=32, unique=True, verbose_name='Слаг'
                    ),
                ),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ('name',),
                'default_related_name': 'tag',
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'author',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='cart',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'recipe',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='cart',
                        to='recipes.recipe',
                    ),
                ),
                (
                    'name',
                    models.CharField(max_length=256, verbose_name='Название'),
                ),
                ('text', models.TextField(verbose_name='Описание')),
                (
                    'image',
                    models.ImageField(
                        upload_to='recipe/images/', verbose_name='Картинка'
                    ),
                ),
                (
                    'cooking_time',
                    models.IntegerField(verbose_name='Время приготовления'),
                ),
            ],
            options={
                'verbose_name': 'Корзина',
                'verbose_name_plural': 'Корзина',
                'ordering': ('-recipe',),
                'default_related_name': 'cart',
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(
                related_name='recipe', to='recipes.Tag', verbose_name='Теги'
            ),
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Корзина',
                'verbose_name_plural': 'Корзина',
                'ordering': ('-recipe',),
                'default_related_name': 'cart',
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
                'ordering': ('user',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'name',
                    models.CharField(max_length=32, verbose_name='Название'),
                ),
                (
                    'slug',
                    models.SlugField(
                        max_length=32, unique=True, verbose_name='Слаг'
                    ),
                ),
            ],
            options={
                'verbose_name': 'Избранное',
                'verbose_name_plural': 'Избранное',
                'ordering': ('author',),
                'default_related_name': 'favorite',
            },
        ),
        migrations.CreateModel(
            name='AmountReceptIngredients',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'amount',
                    models.PositiveIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                limit_value=1
                            )
                        ],
                        verbose_name='Количество',
                    ),
                ),
                (
                    'ingredients',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='amoutn',
                        to='recipes.ingredient',
                        verbose_name='Ингредиент',
                    ),
                ),
                (
                    'recipe',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='amoutn',
                        to='recipes.recipe',
                        verbose_name='Рецепт',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Количество',
                'verbose_name_plural': 'Количество',
                'ordering': ('-amount',),
                'default_related_name': 'amoutn',
            },
        ),
    ]
