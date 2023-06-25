import openai
import json
import os
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic import DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
# PDF Generator
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
# Packages inside projects
from .forms import PantryForm
from .models import Ingredient, Recipe, ChatMessages, Pantry, IngredientType, ShoppingList


openai.api_key = os.environ['openai_api_key']

sample_recipe = {
                    'name': '-',
                    'description': '-',
                    'ingredients': ['-', '-', '-'],
                    'steps': ['-', '-', '-'],
                    'prep_time': '-',
                    'cook_time': '-',
                    'cuisine': '-',
                    'serves': '-',
                }

error_recipe = {
                    'error': 'Our cooks mixed up stuff. Try again.',
                    'name': '-',
                    'description': '-',
                    'ingredients': ['-', '-', '-'],
                    'steps': ['-', '-', '-'],
                    'prep_time': '-',
                    'cook_time': '-',
                    'cuisine': '-',
                    'serves': '-',
                }


def ask_openai(message, history_prompt=[]):
    """
    Sends a request to chatGPT API and gets a response in a configured style with cooking recipe
    :param history_prompt: fills new prompt with history of conversation
    :param message: input on recipe
    :return: content of ChatGPT API response stripped
    """
    prompt = [
        {'role': 'system', 'content': """You are a cooking recipe recommender.
                Please format your response with the following sections: 
                Title, Short Description, Ingredients, Steps, Preparation Time, Cooking Time, Cuisine, Serves."""}
    ]
    if history_prompt:
        for history_prompt_single in history_prompt:
            prompt.append(history_prompt_single)

    prompt.append({'role': 'user', 'content': message})

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=prompt
    )

    answer = response.choices[0].message.content.strip()

    return answer


def parse_response(response):
    """
    Parsing ChatGPT API response into a dict with predefined keys
    :param response: ask_openai function with an input
    :return: parsed dict
    """
    recipe_dict = {}
    try:
        recipe_name, name = response[response.index('Title'):response.index('Short Description')].split(':')
        recipe_dict['name'] = name.strip()

        recipe_description_full = response[response.index('Short Description'):response.index('Ingredients')]
        recipe_description, description = recipe_description_full.split(':')
        recipe_dict['description'] = description.strip()

        recipe_ingredients, ingredients = response[response.index('Ingredients'):response.index('Steps')].split(':', 1)
        ingredients = ingredients.strip()
        ingredients = ingredients.split('\n')
        ingredients = [x for x in ingredients if x != '']
        recipe_dict['ingredients'] = ingredients

        recipe_steps, steps = response[response.index('Steps'):response.index('Preparation Time')].split(':', 1)
        steps = steps.strip()
        steps = steps.split('\n')
        steps = [x for x in steps if x != '']
        recipe_dict['steps'] = steps

        recipe_prep_time, prep_time = response[response.index('Preparation Time'):response.index('Cooking Time')].split(':')
        recipe_dict['prep_time'] = prep_time.strip()

        recipe_cook_time, cook_time = response[response.index('Cooking Time'):response.index('Cuisine')].split(':')
        recipe_dict['cook_time'] = cook_time.strip()

        recipe_cuisine, cuisine = response[response.index('Cuisine'):response.index('Serves')].split(':')
        recipe_dict['cuisine'] = cuisine.strip()

        recipe_serves, serves = response[response.index('Serves'):].split(':')
        recipe_dict['serves'] = serves.strip()

        return recipe_dict

    except ValueError:
        return error_recipe


class CreateRecipeView(LoginRequiredMixin, View):
    """
    View presents forms for recipe creation and allows user to communicate with ChatGPT on changes to it.
    """
    def get(self, request):
        """
        Presents forms to create a recipe.

        :return: Rendered HTML
        """
        recipe = sample_recipe
        pantry_user, created = Pantry.objects.get_or_create(user=request.user)
        pantry = []
        for p in pantry_user.ingredients.all():
            pantry.append(p)

        ctx = {
            'recipe': recipe,
            'pantry': pantry,
        }
        return render(request, 'recipe/create_recipe.html', ctx)

    def post(self, request):
        """
        Updates form with information gathered from ask_openai function parsed trough parse_response function.
        Appends chat history to a prompt from a user about that recipe.

        Saves updated recipe to session under '{user.username}_recipe' key so other views can gather it between them.
        In case connection to ChatGPT fails it renders default view with error.


        :return: Updated rendered HTML view
        """
        user = request.user.username
        session_user_recipe_key = f'{user}_recipe'
        recipe = request.session[session_user_recipe_key]
        try:
            recipe_id = request.session['recipe_id']
        except KeyError:
            recipe_id = -1

        user_message = request.POST.get('user_input')

        messages_history = ChatMessages.objects.filter(user=request.user)
        if recipe_id:
            messages_history = messages_history.filter(recipe=recipe_id).order_by('-created_at')[0:5][::-1]
        history_prompt = []

        if messages_history:


            for message in messages_history:
                history_prompt.append({'role': 'user', 'content': message.message})
                history_prompt.append({'role': 'assistant', 'content': message.response})

        else:
            first_message = ChatMessages.objects.filter(recipe=recipe_id).order_by('created_at').first()
            history_prompt.append({'role': 'user', 'content': first_message.message})
            history_prompt.append({'role': 'assistant', 'content': first_message.response})

        try:
            recipe_response = ask_openai(history_prompt=history_prompt, message=user_message)
            recipe = parse_response(recipe_response)
            if recipe_id > -1:
                chat_message = ChatMessages(user=request.user,
                                            message=user_message,
                                            response=recipe_response,
                                            recipe_id=recipe_id)
                chat_message.save()

            request.session[session_user_recipe_key] = recipe
        except openai.error.RateLimitError:
            try:
                recipe = request.session[session_user_recipe_key]
            except KeyError:
                recipe = error_recipe

            return JsonResponse(recipe)

        return JsonResponse(recipe)


class AddRecipeView(LoginRequiredMixin, View):
    """
    Saves recipe created by view from CreateRecipeView to database.
    """
    def post(self, request):
        """
        Gathers information on recipe from session and stores it into db.

        :return: rendered HTML view of a saved recipe
        """
        user = request.user.username
        session_user_recipe_key = f'{user}_recipe'
        recipe = request.session[session_user_recipe_key]
        recipe_id = request.session['recipe_id']

        recipe_name = recipe['name']
        recipe_description = recipe['description']
        recipe_ingredients = recipe['ingredients']
        recipe_steps = recipe['steps']
        recipe_prep_time = recipe['prep_time']
        recipe_cook_time = recipe['cook_time']
        recipe_cuisine = recipe['cuisine']
        recipe_serves = recipe['serves']

        recipe_user_ingredients = []
        all_ingredients = Ingredient.objects.all()
        for ing in all_ingredients:
            if ing.name.lower() in ''.join(recipe_ingredients).lower():
                recipe_user_ingredients.append(ing)

        recipe_to_save = Recipe.objects.filter(id=recipe_id).first()
        recipe_to_save.name = recipe_name
        recipe_to_save.description = recipe_description
        recipe_to_save.chat_ingredients = recipe_ingredients
        recipe_to_save.steps = recipe_steps
        recipe_to_save.prep_time = recipe_prep_time
        recipe_to_save.cook_time = recipe_cook_time
        recipe_to_save.cuisine = recipe_cuisine
        recipe_to_save.serves = recipe_serves

        recipe_to_save.user_ingredients.clear()

        for ing in recipe_user_ingredients:
            recipe_to_save.user_ingredients.add(ing)
        recipe_to_save.is_saved = 1
        recipe_to_save.save()

        return redirect('recipe_detail', pk=recipe_to_save.id)


@login_required()
def pantry(request):
    """
    Presents form with ingredients to add to user's pantry.
    If user access this view for first time, creates a pantry for him/her.

    :return: rendered HTML forms for pantry management
    """
    user = request.user
    pantry, created = Pantry.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = PantryForm(request.POST, instance=pantry)
        if form.is_valid():
            pantry = form.save(commit=False)
            pantry.ingredients.clear()

            shopping_list = ShoppingList.objects.filter(user=request.user)

            for ingredient in form.cleaned_data['ingredients']:
                pantry.ingredients.add(ingredient)
                for shopping_list_one in shopping_list.all():
                    shopping_list_one.missing_ingredients.remove(ingredient)

            pantry.save()

            return redirect('pantry')

    else:
        form = PantryForm(instance=pantry)

    ingredients_types = IngredientType.objects.all()
    ctx = {
        'form': form,
        'ingredients_types': ingredients_types,
    }
    return render(request, 'recipe/pantry.html', ctx)


@login_required()
def get_ingredient_type_set(request):
    """
    Returns JSON with a list of ingredients in given type.
    Used to filter Pantry View with JS.


    :return: JSON with list under key 'set'
    """
    if request.method == 'POST':
        ingredient_type = request.POST.get('ingredient_type')

        ingredient_type = IngredientType.objects.get(name=ingredient_type).id

        ingredient_type_set = Ingredient.objects.order_by('name').filter(type=ingredient_type)
        ingredients = []
        for ingredient in ingredient_type_set:
            ingredients.append(ingredient.id)

        return JsonResponse({'set': ingredients})


@login_required
def create_new_recipe(request):
    """
    Deletes user's ChatMessage history on unsaved recipes. Creates a new recipe from given instructions.
    Saves it to session and returns JSON with it to site.
    Re-rendering done by JS on front end

    :return: recipe in JSON format
    """
    if request.method == 'POST':
        recipes_to_delete = Recipe.objects.filter(creator=request.user, is_saved=0)
        for rec in recipes_to_delete:
            rec.delete()
        user = request.user.username
        session_user_recipe_key = f'{user}_recipe'

        new_recipe_ingredients = request.POST.getlist('new_recipe_ingredients')[0].split(',')

        ingredients_to_prompt = []
        for ing in new_recipe_ingredients:
            new_ing = Ingredient.objects.filter(id=ing).first()
            ingredients_to_prompt.append(new_ing.name)

        meat_option = request.POST.get('meat_option')
        if meat_option is None:
            meat_option = 'omnivorous'

        meal_type = request.POST.get('meal_type')
        kitchen_type = request.POST.get('kitchen_type')
        additional_info = request.POST.get('additional_info')
        time = request.POST.get('time')

        message = f"""
        Create a new recipe. 
        I have {', '.join([x for x in ingredients_to_prompt])},
        I want a {kitchen_type} style {meal_type},
        made in less than {time} minutes.
        Meal should be {meat_option}.
        {additional_info}.
        """.strip()

        try:
            recipe_response = ask_openai(message=message)
            try:
                recipe = parse_response(recipe_response)

                new_recipe = Recipe.objects.create(creator=request.user)
                request.session['recipe_id'] = new_recipe.id

                chat_message = ChatMessages(user=request.user,
                                            message=message,
                                            response=recipe_response,
                                            recipe=new_recipe)
                chat_message.save()

                request.session[session_user_recipe_key] = recipe
            except ValueError:
                recipe = error_recipe
                return JsonResponse(recipe)

        except openai.error.RateLimitError:
            try:
                recipe = request.session[session_user_recipe_key]
            except KeyError:
                # make alert come up
                recipe = error_recipe

            return JsonResponse(recipe)

        return JsonResponse(recipe)

    return redirect('create_recipe')


class RecipeListView(LoginRequiredMixin, View):
    """
    Renders a view with a list of recipes.
    """
    def get(self, request):
        user = request.user

        user_pantry, created = Pantry.objects.get_or_create(user=user)

        recipes = Recipe.objects.filter(creator=user).filter(is_saved=1).order_by('-updated_at')[1:]
        paginator_recipes = Paginator(recipes, 3)
        page_recipes = request.GET.get('page_recipe')
        recipes = paginator_recipes.get_page(page_recipes)

        last_recipe = Recipe.objects.filter(creator=user).filter(is_saved=1).order_by('-updated_at').first()

        is_in_pantry = []
        last_recipe_ingredients = {}
        if last_recipe:
            for rec_ing in last_recipe.user_ingredients.all():
                if rec_ing in user_pantry.ingredients.all():
                    is_in_pantry.append(rec_ing)
            try:
                value = round(len(is_in_pantry) / len(last_recipe.user_ingredients.all()) * 100, 1)
                last_recipe_ingredients[last_recipe.id] = value
            except ZeroDivisionError:
                last_recipe_ingredients[last_recipe.id] = 100

        amount_of_ingredients = {}

        if recipes:
            for rec in recipes:
                is_in_pantry = []
                for rec_ing in rec.user_ingredients.all():
                    if rec_ing in user_pantry.ingredients.all():
                        is_in_pantry.append(rec_ing)
                try:
                    amount_of_ingredients[rec.id] = round(len(is_in_pantry) / len(rec.user_ingredients.all()) * 100, 1)
                except ZeroDivisionError:
                    amount_of_ingredients[rec.id] = 100

        other_recipes = Recipe.objects.exclude(creator=user).filter(is_saved=1).annotate(count=Count('likes')).order_by('-count')
        paginator_other_recipes = Paginator(other_recipes, 4)
        page_other_recipes = request.GET.get('page_other_recipes')
        other_recipes = paginator_other_recipes.get_page(page_other_recipes)

        if other_recipes:
            for rec in other_recipes:
                is_in_pantry = []
                for rec_ing in rec.user_ingredients.all():
                    if rec_ing in user_pantry.ingredients.all():
                        is_in_pantry.append(rec_ing)

                try:
                    amount_of_ingredients[rec.id] = round(len(is_in_pantry) / len(rec.user_ingredients.all()) * 100, 1)
                except ZeroDivisionError:
                    amount_of_ingredients[rec.id] = 100

        ctx = {
            'last_recipe': last_recipe,
            'last_recipe_ingredients': last_recipe_ingredients,
            'recipes': recipes,
            'amount_of_ingredients': amount_of_ingredients,
            'other_recipes': other_recipes
        }
        return render(request, 'recipe/recipes.html', ctx)


class RecipeView(LoginRequiredMixin, DetailView):
    """
    Renders detail view of a recipe.
    """
    model = Recipe
    context_object_name = 'recipe'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_pantry = Pantry.objects.filter(user=self.request.user).first()
        ingredients_in_pantry = user_pantry.ingredients.all()
        recipe = context['object']
        recipe_ingredients = recipe.user_ingredients.all()

        total_likes = recipe.total_likes()

        missing_ingredients = []
        for rec_ing in recipe_ingredients:
            if rec_ing not in ingredients_in_pantry:
                missing_ingredients.append(rec_ing)
        context['missing_ingredients'] = missing_ingredients
        context['total_likes'] = total_likes

        return context


class RecipeUpdateView(LoginRequiredMixin, View):
    """
    Renders forms for editing recipe. Changing and committing recipes managed by separated views.
    """
    def get(self, request, pk):
        """
        Renders specific recipe view with options to send a comment on it to ChatGPT in order to change it.
        Gathers recipe from db based on pk.

        :param pk: id of a recipe
        :return: rendered forms for updating recipe
        """
        request.session['recipe_id'] = pk
        user = request.user.username
        recipe = Recipe.objects.filter(id=pk).first()
        session_user_recipe_key = f'{user}_recipe'
        request.session[session_user_recipe_key] = {
                    'name': recipe.name,
                    'description': recipe.description,
                    'ingredients': recipe.chat_ingredients,
                    'steps': recipe.steps,
                    'prep_time': recipe.prep_time,
                    'cook_time': recipe.cook_time,
                    'cuisine': recipe.cuisine,
                    'serves': recipe.serves,
                }

        ctx = {
            'recipe': recipe
        }
        return render(request, 'recipe/recipe_edit.html', ctx)


class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    """
    Deletes recipe.
    Link to view renders only if logged user is the same as creator of the recipe.
    """
    model = Recipe
    success_url = '/recipes/'
    template_name = 'recipe/recipe_delete.html'


class RecipeAddAsNew(LoginRequiredMixin, View):
    """
    Available from Edit View to save recipe to db as a new one.
    Gathers information on recipe from session created by CreateRecipeView
    """
    def post(self, request):
        """
        Saves Recipe based on existing one to the db and redirects to it detail view.

        :return: rendered HTML view of a saved recipe
        """
        user = request.user.username
        session_user_recipe_key = f'{user}_recipe'
        recipe = request.session[session_user_recipe_key]
        base_recipe_id = request.session['recipe_id']

        recipe_name = recipe['name']
        recipe_description = recipe['description']
        recipe_ingredients = recipe['ingredients']
        recipe_steps = recipe['steps']
        recipe_prep_time = recipe['prep_time']
        recipe_cook_time = recipe['cook_time']
        recipe_cuisine = recipe['cuisine']
        recipe_serves = recipe['serves']

        recipe_user_ingredients = []
        all_ingredients = Ingredient.objects.all()
        for ing in all_ingredients:
            if ing.name.lower() in ''.join(recipe_ingredients).lower():
                recipe_user_ingredients.append(ing)

        recipe_to_save = Recipe.objects.create(creator=request.user)

        base_recipe = Recipe.objects.filter(id=base_recipe_id).first()

        last_recipe_message = ChatMessages.objects.filter(recipe=base_recipe).order_by('-created_at').first()
        new_chat_message = ChatMessages.objects.create(
            user=request.user,
            message=last_recipe_message.message,
            response=last_recipe_message.response,
            recipe_id=recipe_to_save.id)

        recipe_to_save.name = recipe_name
        recipe_to_save.description = recipe_description
        recipe_to_save.chat_ingredients = recipe_ingredients
        recipe_to_save.steps = recipe_steps
        recipe_to_save.prep_time = recipe_prep_time
        recipe_to_save.cook_time = recipe_cook_time
        recipe_to_save.cuisine = recipe_cuisine
        recipe_to_save.serves = recipe_serves
        for ing in recipe_user_ingredients:
            recipe_to_save.user_ingredients.add(ing)
        recipe_to_save.is_saved = 1
        recipe_to_save.save()

        return redirect('recipe_detail', pk=recipe_to_save.id)


class AddMissingIngredientsView(LoginRequiredMixin, View):
    """
    Available from recipe detail view.
    Saves ingredients either to pantry from this level
    or creates a shopping list instance for user with missing ingredients.
    If ingredients added to pantry from recipe detail view, they are removed from shopping list
    """
    def post(self, request):
        recipe_id = request.POST.get('recipe_id')
        recipe = Recipe.objects.filter(id=recipe_id).first()
        missing_ingredients = request.POST.getlist('missing_ingredient')

        if 'add_to_pantry' in request.POST:
            user_pantry, created = Pantry.objects.get_or_create(user=request.user)
            shopping_list = ShoppingList.objects.filter(user=request.user)

            for ing_to_pantry in missing_ingredients:
                user_pantry.ingredients.add(ing_to_pantry)
                for shopping_list_one in shopping_list.all():
                    shopping_list_one.missing_ingredients.remove(ing_to_pantry)

            return redirect('recipe_detail', pk=recipe_id)

        if 'add_to_shopping_list' in request.POST:
            shopping_list, created = ShoppingList.objects.get_or_create(user=request.user, recipe=recipe)
            for ing_to_shop in missing_ingredients:
                shopping_list.missing_ingredients.add(ing_to_shop)

            return redirect('shopping_list')


class ShoppingListView(LoginRequiredMixin, View):
    """
    View presents shopping lists for user divided by recipes.
    """
    def get(self, request):
        """
        Renders View with shopping lists.
        On request deletes shopping lists without missing ingredients.

        :return: rendered HTML view
        """
        shopping_lists = ShoppingList.objects.filter(user=request.user)
        for shopping_list in shopping_lists:
            if len(shopping_list.missing_ingredients.all()) == 0:
                shopping_list.delete()

        shopping_lists = ShoppingList.objects.filter(user=request.user)
        ctx = {
            'shopping_lists': shopping_lists
        }
        return render(request, 'recipe/shoppinglist_list.html', ctx)


class ShoppingListDeleteView(LoginRequiredMixin, DeleteView):
    """
    Deletes Shopping List.
    """
    model = ShoppingList
    success_url = '/shoppinglist/'
    template_name = 'recipe/shoppinglist_delete.html'


@login_required()
def shopping_pdf(request):
    """
    Creates a PDF out of selected shopping lists or all items from all shopping lists

    :return: downloadable PDF with shopping lists
    """
    if request.method == 'POST':
        if 'get_all' in request.POST:
            all_shopping_lists = ShoppingList.objects.filter(user=request.user)

            if len(all_shopping_lists.all()) > 0:

                buf = io.BytesIO()
                c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
                text_obj = c.beginText()
                text_obj.setTextOrigin(inch, inch)
                text_obj.setFont('Helvetica', 14)

                text_obj.textLine('Your Whole Shopping List:')
                text_obj.textLine()
                list_to_print = []

                for shopping_list in all_shopping_lists:
                    for ing in shopping_list.missing_ingredients.all():
                        for chat_ing in shopping_list.recipe.chat_ingredients:
                            if ing.name.lower() in chat_ing.lower():
                                list_to_print.append(chat_ing)

                for item in list_to_print:
                    text_obj.textLine(item)

                text_obj.textLine()
                text_obj.textLine('Enjoy your meal. Come back soon.')

                c.drawText(text_obj)
                c.showPage()
                c.save()
                buf.seek(0)

                return FileResponse(buf, as_attachment=True, filename=f'{request.user.username}\'s Shopping List.pdf')

        lists_to_print = request.POST.getlist('shopping_list_to_pdf')

        if len(lists_to_print) > 0:
            buf = io.BytesIO()
            c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
            text_obj = c.beginText()
            text_obj.setTextOrigin(inch, inch)
            text_obj.setFont('Helvetica', 14)

            text_obj.textLine('Your Shopping List')
            text_obj.textLine()
            for s_l_id in lists_to_print:
                list_to_print = []
                text_obj.textLine('For:')
                shopping_list = ShoppingList.objects.filter(id=s_l_id).first()
                text_obj.textLine(shopping_list.recipe.name)
                text_obj.textLine('you need:')
                for ing in shopping_list.missing_ingredients.all():
                    for chat_ing in shopping_list.recipe.chat_ingredients:
                        if ing.name.lower() in chat_ing.lower():
                            list_to_print.append(chat_ing)

                for item in list_to_print:
                    text_obj.textLine(item)
                text_obj.textLine()

            text_obj.textLine()
            text_obj.textLine('Enjoy your meal. Come back soon.')

            c.drawText(text_obj)
            c.showPage()
            c.save()
            buf.seek(0)

            return FileResponse(buf, as_attachment=True, filename=f'{request.user.username}\'s Shopping List.pdf')

        else:
            return redirect('shopping_list')


class RecipeLikeView(LoginRequiredMixin, View):
    """
    Adds likes to recipe from current user
    """
    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        recipe.likes.add(request.user)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class RecipeDislikeView(LoginRequiredMixin, View):
    """
    Removes likes to recipe from current user
    """
    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        recipe.likes.remove(request.user)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
