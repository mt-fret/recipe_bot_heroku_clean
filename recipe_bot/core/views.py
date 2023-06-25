from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from recipe.models import Recipe

from .forms import SignUpForm


def index(request):
    return render(request, 'core/index.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect('index')

    else:
        form = SignUpForm()

    return render(request, 'core/signup.html', {'form': form})


@login_required
def user_view(request, pk):
    user = User.objects.filter(id=pk).first()
    recipes = Recipe.objects.filter(creator=user)
    likes = 0
    for recipe in recipes:
        likes += recipe.total_likes()

    ctx = {
        'user': user,
        'no_of_recipes': len(recipes),
        'likes': likes
    }

    return render(request, 'core/user_view.html', ctx)
