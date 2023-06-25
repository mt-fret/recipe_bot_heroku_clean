# Generated by Django 4.2.1 on 2023-06-02 18:24

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0010_alter_recipe_cuisine_alter_recipe_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='chat_ingredients',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='steps',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=500), blank=True, null=True, size=None),
        ),
    ]
