# Generated by Django 4.0.7 on 2022-08-05 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_dataset_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='algorithm',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='algorithm',
            name='formula_score',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Формула оценивающей метрики'),
        ),
    ]