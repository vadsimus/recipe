from django import forms
from .models import Ingredient, Recipe


class IngredientForm(forms.Form):
    ingredient_quantity = forms.IntegerField(min_value=1)

    # def clean_name(self):
    #     name = self.cleaned_data.get('name')
    #     if Ingredient.objects.filter(name=name).exists():
    #         raise forms.ValidationError("This ingredient already exists.")
    #     return name


class RecipeForm(forms.ModelForm):
    ingredients = forms.ModelMultipleChoiceField(queryset=Ingredient.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Recipe
        fields = ['name', 'ingredients']

    def clean(self):
        cleaned_data = super().clean()
        ingredients = cleaned_data.get('ingredients')
        if not ingredients:
            raise forms.ValidationError("Please select at least one ingredient.")
        return cleaned_data
