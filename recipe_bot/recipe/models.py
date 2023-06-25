from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField


class IngredientType(models.Model):
    """
    Model stores types ingredients.
    """
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Model stores ingredients with relation to their type.
    """
    name = models.CharField(max_length=255)
    type = models.ForeignKey(IngredientType, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class Pantry(models.Model):
    """
    Model stores user pantry with relation to ingredients they have. One pantry per user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(Ingredient)


class Recipe(models.Model):
    """
    Model stores recipes.
    is_saved field is True if user specifically decides to store that recipe.
    """
    name = models.CharField(max_length=255, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(null=True)
    user_ingredients = models.ManyToManyField(Ingredient)
    chat_ingredients = ArrayField(models.CharField(max_length=255), blank=True, null=True)
    steps = ArrayField(models.CharField(max_length=500), blank=True, null=True)
    cook_time = models.CharField(max_length=50, null=True)
    prep_time = models.CharField(max_length=50, null=True)
    cuisine = models.CharField(max_length=100, null=True)
    serves = models.CharField(max_length=250, null=True)
    likes = models.ManyToManyField(User, related_name='recipe_likes')
    is_saved = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_likes(self):
        return self.likes.count()


class ChatMessages(models.Model):
    """
    Model stores conversation with ChatGPT history divided by user and recipes.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ShoppingList(models.Model):
    """
    Model stores ingredients user is missing from certain recipes.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    missing_ingredients = models.ManyToManyField(Ingredient)
