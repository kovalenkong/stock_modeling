# Generated by Django 4.0.7 on 2022-08-04 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_user_managers_remove_user_username_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='algorithm',
            name='is_public',
            field=models.BooleanField(default=False, verbose_name='Публичный'),
        ),
    ]