from rest_framework import serializers
from .models import Ingredient, Recipe, IngredientRecipe

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'cost']


class IngredientRecipeSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()  # Nesting IngredientSerializer

    class Meta:
        model = IngredientRecipe
        fields = ['ingredient', 'ingredient_amount']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(source='ingredientrecipe_set', many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image_url', 'description', 'ingredients']
