import pytest
from recipe.models import Ingredient, IngredientType, Pantry, Recipe, ShoppingList
from django.http import JsonResponse
from django.shortcuts import reverse


# test logged user into Pantry View and pantry is empty
@pytest.mark.django_db
def test_pantry(client, user):
    client.force_login(user)
    r = client.get('/pantry/')
    pantry, created = Pantry.objects.get_or_create(user=user)

    assert r.status_code == 200
    assert len(pantry.ingredients.all()) == 0


# test logged user can add ingredients to Pantry
@pytest.mark.django_db
def test_add_pantry(client, user, pantry, ingredient, ingredient2):
    client.force_login(user)
    form_data = {
        'ingredients': [ingredient2.id, ingredient.id]
    }
    r = client.post('/pantry/', form_data)
    pantry.refresh_from_db()

    assert r.status_code == 302
    assert len(pantry.ingredients.all()) == 2
    assert ingredient in pantry.ingredients.all()


# test getting set return JSON
@pytest.mark.django_db
def test_get_ingredient_type_set(client, user, ingredient_type):
    client.force_login(user)
    data = {
        'ingredient_type': ingredient_type.name
    }
    r = client.post('/get_set/', data)

    assert isinstance(r, JsonResponse)


# test not logged user access get_set
@pytest.mark.django_db
def test_get_ingredient_type_set_not_logged(client, user, ingredient_type):
    data = {
        'ingredient_type': ingredient_type.name
    }
    r = client.post('/get_set/', data)

    assert r.status_code == 302


# test accessing create_recipe view and pantry is empty
@pytest.mark.django_db
def test_create_recipe_get(client, user, pantry):
    client.force_login(user)
    r = client.get('/create_recipe/')

    assert r.status_code == 200
    assert len(r.context['pantry']) == 0


# test accessing create new recipe view via get
@pytest.mark.django_db
def test_create_new_recipe_view_get(client, user):
    client.force_login(user)

    r = client.get('/create_new_recipe/')

    assert r.status_code == 302
    assert 'create_recipe' in r.url


# test create new recipe view (commented out - ChatGPT tests take too much time)
# @pytest.mark.django_db
# def test_create_new_recipe(client, user, ingredient, ingredient2):
#     client.force_login(user)
#     data = {
#         'meal_type': 'lunch',
#         'kitchen_type': 'Mexican',
#         'time': '30',
#         'additional_info': '',
#         'new_recipe_ingredients': [ingredient.id, ingredient2.id],
#     }
#
#     new_recipe = Recipe.objects.all()
#     r = client.post('/create_new_recipe/', data)
#
#     assert len(new_recipe) > 0
#     assert new_recipe.first().is_saved == 0
#     assert isinstance(r, JsonResponse)


# test creating a new recipe (commented out - ChatGPT tests take too much time)
# @pytest.mark.django_db
# def test_create_recipe_post(client, user, pantry, ingredient, ingredient2):
#     client.force_login(user)
#     pantry.ingredients.add(ingredient2.id)
#     pantry.ingredients.add(ingredient.id)
#     data = {
#         'user_input': 'I have apples, bacon and pasta. Create a mexican lunch i can cook in 30 minutes'
#     }
#     r = client.post('/create_recipe/', data)
#
#     assert isinstance(r, JsonResponse)


# test saving new recipe
@pytest.mark.django_db
def test_add_recipe(client, user, ingredient, ingredient2):
    client.force_login(user)
    recipe = Recipe.objects.create(
        name='Recipe Test',
        description='Desc Test',
        creator=user
    )

    session = client.session

    session['recipe_id'] = recipe.pk
    session_user_recipe_key = f'{user.username}_recipe'
    session[session_user_recipe_key] = {
                    'name': 'Test Recipe',
                    'description': '-',
                    'ingredients': [ingredient.name, ingredient2.name, '-'],
                    'steps': ['-', '-', '-'],
                    'prep_time': '-',
                    'cook_time': '-',
                    'cuisine': '-',
                    'serves': '3',
                }
    session.save()

    r = client.post('/add_recipe/')

    recipe.refresh_from_db()

    assert recipe.name == 'Test Recipe'
    assert len(recipe.user_ingredients.all()) == 2
    assert recipe.id == 1
    assert recipe.is_saved == 1
    assert recipe.serves == '3'
    assert r.status_code == 302


# test error when no recipe in session (accessing without creation first)
@pytest.mark.django_db
def test_add_recipe_no_sess(client, user, recipe):
    with pytest.raises(KeyError):
        client.force_login(user)
        client.post('/add_recipe/')


# recipes view get
@pytest.mark.django_db
def test_recipes_get(client, user, user2, saved_recipe, saved_recipe2, ingredient, ingredient2):
    saved_recipe.user_ingredients.add(ingredient)
    saved_recipe2.user_ingredients.add(ingredient2)
    client.force_login(user)
    r = client.get('/recipes/')

    assert r.status_code == 200
    assert r.context['last_recipe'] == saved_recipe
    assert saved_recipe2 in r.context['other_recipes'].object_list


# user tries to access recipes not logged in
@pytest.mark.django_db
def test_recipes_not_logged(client, user):
    r = client.get('/recipes/')

    assert r.status_code == 302
    assert 'login' in r.url


# test recipe detail view and shows missing ingredients
@pytest.mark.django_db
def test_recipe_detail_get(client, user, saved_recipe, pantry, ingredient):
    client.force_login(user)
    saved_recipe.user_ingredients.add(ingredient.id)

    r = client.get(f'/recipe/{saved_recipe.id}/')

    assert r.status_code == 200
    assert ingredient in r.context['missing_ingredients']


# test recipe detail view and user has all ingredients
@pytest.mark.django_db
def test_recipe_detail_all_ingredientes(client, user, saved_recipe, pantry, ingredient):
    client.force_login(user)
    saved_recipe.user_ingredients.add(ingredient.id)

    pantry.ingredients.add(ingredient.id)

    r = client.get(f'/recipe/{saved_recipe.id}')

    assert 'missing_ingredients' not in r.context


# test recipe_update view
@pytest.mark.django_db
def test_recipe_update(client, user, saved_recipe):
    client.force_login(user)
    url = reverse('recipe_update', args=(saved_recipe.id,))

    r = client.get(url)

    assert r.status_code == 200
    assert r.context['recipe'].id == saved_recipe.id
    assert client.session['recipe_id'] == saved_recipe.id


# test recipe_update view without logging in
@pytest.mark.django_db
def test_recipe_update_logout(client, user, saved_recipe):
    url = reverse('recipe_update', args=(saved_recipe.id,))

    r = client.get(url)
    assert r.status_code == 302
    assert 'login' in r.url


# test recipe delete view access
@pytest.mark.django_db
def test_recipe_delete(client, user, saved_recipe):
    client.force_login(user)
    url = reverse('recipe_delete', args=(saved_recipe.id,))

    r = client.get(url)

    assert r.status_code == 200
    assert r.context['recipe'].id == saved_recipe.id


# test recipe delete view without logging in
@pytest.mark.django_db
def test_recipe_delete_logout(client, user, saved_recipe):
    url = reverse('recipe_delete', args=(saved_recipe.id,))

    r = client.get(url)
    assert r.status_code == 302
    assert 'login' in r.url


# test add recipe as new view
@pytest.mark.django_db
def test_add_recipe_as_new(client, user, saved_recipe, ingredient, ingredient2):
    client.force_login(user)

    session = client.session

    session_user_recipe_key = f'{user.username}_recipe'
    session[session_user_recipe_key] = {
                    'name': 'Test Recipe',
                    'description': '-',
                    'ingredients': [ingredient.name, ingredient2.name, '-'],
                    'steps': ['-', '-', '-'],
                    'prep_time': '-',
                    'cook_time': '-',
                    'cuisine': '-',
                    'serves': '3',
                }

    session.save()

    r = client.post('/add_recipe_as_new/')

    assert r.status_code == 302
    assert len(Recipe.objects.all()) == 2


# test if added recipe is the same as the base one
@pytest.mark.django_db
def test_add_recipe_as_new_same(client, user, saved_recipe):
    client.force_login(user)
    session = client.session
    session_user_recipe_key = f'{user.username}_recipe'
    session[session_user_recipe_key] = {
                    'name': saved_recipe.name,
                    'description': saved_recipe.description,
                    'ingredients': saved_recipe.chat_ingredients,
                    'steps': saved_recipe.steps,
                    'prep_time': saved_recipe.prep_time,
                    'cook_time': saved_recipe.cook_time,
                    'cuisine': saved_recipe.cuisine,
                    'serves': saved_recipe.serves,
                }

    session.save()

    r = client.post('/add_recipe_as_new/')

    new_recipe = Recipe.objects.get(id=r.url[-3:-1])

    assert r.status_code == 302
    assert saved_recipe.name == new_recipe.name
    assert saved_recipe.description == new_recipe.description
    assert saved_recipe.cuisine == new_recipe.cuisine


# test adding ingredients to shopping list
@pytest.mark.django_db
def test_shopping_list(client, user, saved_recipe, ingredient, ingredient2):
    client.force_login(user)

    data = {
        'missing_ingredient': [ingredient.id, ingredient2.id],
        'add_to_shopping_list': 1,
        'recipe_id': saved_recipe.id
    }
    r = client.post('/add_missing_ingredients/', data)

    shopping_list = ShoppingList.objects.filter(user=user, recipe=saved_recipe).first()

    assert r.status_code == 302
    assert ingredient in shopping_list.missing_ingredients.all()
    assert len(shopping_list.missing_ingredients.all()) == 2


# test adding to pantry removes items from shopping list
@pytest.mark.django_db
def test_shopping_list_pantry(client, user, saved_recipe, ingredient, ingredient2):
    client.force_login(user)

    data = {
        'missing_ingredient': [ingredient.id, ingredient2.id],
        'add_to_shopping_list': 1,
        'recipe_id': saved_recipe.id
    }
    client.post('/add_missing_ingredients/', data)

    data = {
        'missing_ingredient': [ingredient.id],
        'add_to_pantry': 1,
        'recipe_id': saved_recipe.id
    }

    r = client.post('/add_missing_ingredients/', data)

    shopping_list = ShoppingList.objects.filter(user=user, recipe=saved_recipe).first()

    assert r.status_code == 302
    assert ingredient not in shopping_list.missing_ingredients.all()
    assert ingredient2 in shopping_list.missing_ingredients.all()


# test shopping recipes view
@pytest.mark.django_db
def test_shopping_list_list_view(client, user, saved_recipe, ingredient, ingredient2):
    client.force_login(user)

    shopping_list = ShoppingList.objects.create(
        user=user,
        recipe=saved_recipe,
    )

    shopping_list.missing_ingredients.add(ingredient)
    shopping_list.missing_ingredients.add(ingredient2)

    r = client.get('/shoppinglist/')

    assert r.status_code == 200
    assert shopping_list in r.context['shopping_lists']


# test shopping recipes views if user has no recipes
@pytest.mark.django_db
def test_shopping_list_no_lists(client, user):
    client.force_login(user)

    r = client.get('/shoppinglist/')

    assert r.status_code == 200
    assert len(r.context['shopping_lists']) == 0


# test deleting shopping list
@pytest.mark.django_db
def test_shopping_list_delete(client, user, saved_recipe,ingredient):
    client.force_login(user)

    shopping_list = ShoppingList.objects.create(
        user=user,
        recipe=saved_recipe
    )

    shopping_list.missing_ingredients.add(ingredient)
    url = reverse('shoppinglist_delete', args=(shopping_list.id,))

    r = client.get(url)

    assert r.status_code == 200
    assert r.context['shoppinglist'].id == shopping_list.id


# test deleteing shopping list without being logged in
@pytest.mark.django_db
def test_shopping_list_delete_not_logged(client, user, saved_recipe, ingredient):
    shopping_list = ShoppingList.objects.create(
        user=user,
        recipe=saved_recipe
    )

    shopping_list.missing_ingredients.add(ingredient)
    url = reverse('shoppinglist_delete', args=(shopping_list.id,))

    r = client.get(url)
    assert r.status_code == 302
    assert 'login' in r.url


# test liking recipe
@pytest.mark.django_db
def test_recipe_like(client, user, saved_recipe):
    client.force_login(user)

    url = reverse('recipe_like', args=(saved_recipe.id,))
    r = client.post(url)

    assert saved_recipe.total_likes() == 1
    assert r.status_code == 302


# test once liked recipe doesn't count it twice
@pytest.mark.django_db
def test_recipe_like_twice(client, user, saved_recipe):
    client.force_login(user)
    saved_recipe.likes.add(user.id)

    url = reverse('recipe_like', args=(saved_recipe.id,))
    r = client.post(url)

    assert saved_recipe.total_likes() == 1
    assert r.status_code == 302


# test disliking recipe
@pytest.mark.django_db
def test_recipe_dislike(client, user, saved_recipe):
    client.force_login(user)
    saved_recipe.likes.add(user.id)

    url = reverse('recipe_dislike', args=(saved_recipe.id,))
    r = client.post(url)

    assert saved_recipe.total_likes() == 0
    assert r.status_code == 302


# test recipe keeps rest of the likes
@pytest.mark.django_db
def test_recipe_dislike_keeps(client, user, user2, saved_recipe):
    client.force_login(user)
    saved_recipe.likes.add(user2.id)

    url = reverse('recipe_dislike', args=(saved_recipe.id,))
    r = client.post(url)

    assert saved_recipe.total_likes() == 1
    assert r.status_code == 302


# test get pdf creates a pdf
@pytest.mark.django_db
def test_shopping_pdf_get_list(client, user, saved_recipe, ingredient, ingredient2):
    client.force_login(user)

    saved_recipe.chat_ingredients = [ingredient, ingredient2]
    print(saved_recipe.chat_ingredients)
    shopping_list = ShoppingList.objects.create(
        user=user,
        recipe=saved_recipe,
    )
    print(user.shoppinglist_set)


    shopping_list.missing_ingredients.add(ingredient.id)
    shopping_list.missing_ingredients.add(ingredient2.id)

    data = {
        'get_all': True,
    }
    file_name = f'{user.username}\'s Shopping List.pdf'
    r = client.post('/shopping_pdf/', data)

    assert r.status_code == 200
    assert r.headers['Content-Type'] == 'application/pdf'
    assert file_name in r.headers['Content-Disposition']


# test downloading pdf not logged in
@pytest.mark.django_db
def test_shopping_pdf_not_logged(client, user):
    data = {
        'get_all': True,
    }

    r = client.post('/shopping_pdf/', data)

    assert r.status_code == 302
    assert 'login' in r.url
