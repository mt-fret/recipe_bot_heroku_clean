# Generated by Django 4.2.1 on 2023-05-28 11:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipe', '0005_pantry_has_it'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pantry',
            name='user',
        ),
        migrations.AddField(
            model_name='pantry',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]