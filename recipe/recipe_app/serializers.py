from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Ingredient, Recipe, IngredientRecipe


class IngredientRecipeWriteSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    quantity = serializers.IntegerField(source='ingredient_amount')

    class Meta:
        model = IngredientRecipe
        fields = ['ingredient', 'quantity']


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
    ingredients = IngredientRecipeWriteSerializer(many=True, source='ingredient_recipes', required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'description', 'ingredients']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredient_recipes', [])
        user = validated_data.pop('user', self.context['request'].user)
        recipe = Recipe.objects.create(user=user, **validated_data)
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['ingredient']
            quantity = ingredient_data['ingredient_amount']
            if ingredient.user != user:
                raise serializers.ValidationError(f"Ingredient with id {ingredient.id} does not belong to the user.")
            IngredientRecipe.objects.create(recipe=recipe, ingredient=ingredient, ingredient_amount=quantity)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredient_recipes', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if ingredients_data is not None:
            instance.ingredient_recipes.all().delete()
            user = self.context['request'].user
            for ingredient_data in ingredients_data:
                ingredient = ingredient_data['ingredient']
                quantity = ingredient_data['ingredient_amount']
                if ingredient.user != user:
                    raise serializers.ValidationError(
                        f"Ingredient with id {ingredient.id} does not belong to the user."
                    )
                IngredientRecipe.objects.create(recipe=instance, ingredient=ingredient, ingredient_amount=quantity)
        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['ingredients'] = IngredientRecipeSerializer(
            instance.ingredient_recipes.all(), many=True, context=self.context
        ).data
        if instance.image:
            request = self.context.get('request')
            if request:
                rep['image'] = request.build_absolute_uri(instance.image.url)
        return rep


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
