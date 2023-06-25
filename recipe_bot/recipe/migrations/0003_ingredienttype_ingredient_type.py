# Generated by Django 4.2.1 on 2023-05-28 09:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0002_recipe_chatmessages'),
    ]

    operations = [
        migrations.CreateModel(
            name='IngredientType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='ingredient',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='recipe.ingredienttype'),
        ),
    ]
