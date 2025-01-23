from django.contrib.auth.models import User
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
        fields = ['id', 'name', 'image', 'description', 'ingredients']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.image:
            request = self.context.get('request')
            if request:
                representation['image'] = request.build_absolute_uri(instance.image.url)
        return representation


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Скрываем пароль
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
