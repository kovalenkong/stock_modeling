# Generated by Django 4.0.7 on 2022-09-07 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_algorithm_description_alter_algorithm_formula_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='Почта'),
        ),
    ]
