# Generated by Django 4.2.1 on 2023-05-28 11:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0006_remove_pantry_user_pantry_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pantry',
            name='has_it',
        ),
    ]
