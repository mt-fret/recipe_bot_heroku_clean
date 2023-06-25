from django import forms

from .models import Pantry, Ingredient


class PantryForm(forms.ModelForm):
    """
    Form to present user with ingredients.
    """
    class Meta:
        model = Pantry
        fields = ['ingredients']

    ingredients = forms.ModelMultipleChoiceField(queryset=Ingredient.objects.order_by('name'), label='Ingredients',
                                                 widget=forms.CheckboxSelectMultiple)
