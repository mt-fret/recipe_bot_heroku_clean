# Generated by Django 4.2.1 on 2023-06-02 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0009_chatmessages_recipe_recipe_cook_time_recipe_creator_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cuisine',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='serves',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='user_ingredients',
            field=models.ManyToManyField(null=True, to='recipe.ingredient'),
        ),
    ]