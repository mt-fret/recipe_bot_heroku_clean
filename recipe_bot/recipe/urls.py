from django.urls import path, re_path
from . import views

urlpatterns = [
    path('create_recipe/', views.CreateRecipeView.as_view(), name='create_recipe'),
    path('create_new_recipe/', views.create_new_recipe, name='create_new_recipe'),

    path('pantry/', views.pantry, name='pantry'),
    path('add_missing_ingredients/', views.AddMissingIngredientsView.as_view(), name='add_missing_ingredients'),
    path('shoppinglist/', views.ShoppingListView.as_view(), name='shopping_list'),
    path('shopping_pdf/', views.shopping_pdf, name='shopping_pdf'),
    path('shoppinglist/<int:pk>/delete/', views.ShoppingListDeleteView.as_view(), name='shoppinglist_delete'),

    path('recipes/', views.RecipeListView.as_view(), name='recipes'),
    path('recipe/<int:pk>/', views.RecipeView.as_view(), name='recipe_detail'),
    path('recipe/<int:pk>/edit/', views.RecipeUpdateView.as_view(), name='recipe_update'),
    path('recipe/<int:pk>/delete/', views.RecipeDeleteView.as_view(), name='recipe_delete'),
    path('recipe/<int:pk>/like/', views.RecipeLikeView.as_view(), name='recipe_like'),
    path('recipe/<int:pk>/dislike', views.RecipeDislikeView.as_view(), name='recipe_dislike'),

    path('add_recipe/', views.AddRecipeView.as_view(), name='add_recipe'),
    path('add_recipe_as_new/', views.RecipeAddAsNew.as_view(), name='add_recipe_as_new'),

    path('get_set/', views.get_ingredient_type_set, name='get_set'),

]
