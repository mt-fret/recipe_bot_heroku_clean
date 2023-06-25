from django.contrib import admin

from .models import Ingredient, IngredientType, Recipe

admin.site.register(IngredientType)
admin.site.register(Recipe)

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
