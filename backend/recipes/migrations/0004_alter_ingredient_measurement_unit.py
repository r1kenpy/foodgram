# Generated by Django 3.2.3 on 2024-07-21 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20240721_2342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(max_length=64, verbose_name='Единица измерения'),
        ),
    ]
