import pytest
from django.test import Client
from django.contrib.auth.models import User
from recipe.models import Pantry, IngredientType, Ingredient, Recipe, ShoppingList


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user():
    user = User.objects.create_user(
        username='test_user',
        password='test_password'
    )

    return user


@pytest.fixture
def user2():
    user = User.objects.create_user(
        username='test_user2',
        password='test_password2'
    )

    return user


@pytest.fixture
def ingredient_type():
    i_t = IngredientType.objects.create(
        name='Vegetables'
    )

    return i_t


@pytest.fixture
def ingredient():
    i = Ingredient.objects.create(
        name='Apple',
    )

    return i


@pytest.fixture
def ingredient2():
    i = Ingredient.objects.create(
        name='Orange',
    )

    return i


@pytest.fixture
def pantry(user, ingredient):
    p = Pantry.objects.create(
        user=user
    )

    return p


@pytest.fixture
def recipe(user):
    r = Recipe.objects.create(
        name='Test Recipe',
        creator=user,
        description='Test Description',
    )
    return r


@pytest.fixture
def saved_recipe(user):
    r = Recipe.objects.create(
        name='Test Recipe',
        creator=user,
        description='Test Description',
        is_saved=1
    )
    return r


@pytest.fixture()
def saved_recipe2(user2):
    r = Recipe.objects.create(
        name='Test Recipe2',
        creator=user2,
        description='Test Description2',
        is_saved=1
    )
    return r

