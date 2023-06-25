# Generated by Django 4.2.1 on 2023-06-06 19:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0015_recipe_likes'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipe',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
