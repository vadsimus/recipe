from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from recipe_app.models import Recipe, Ingredient, IngredientRecipe


class RecipeAPITestCase(APITestCase):

    def setUp(self):
        # create user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

        # create ingredients
        self.ingredient1 = Ingredient.objects.create(name="Salt", cost=0.5, user=self.user)
        self.ingredient2 = Ingredient.objects.create(name="Sugar", cost=1.0, user=self.user)

    def test_create_recipe_with_ingredients(self):
        url = '/recipes/'
        data = {
            "name": "Test Recipe",
            "description": "Test description",
            "image_url": "http://example.com/image.jpg",
            "ingredients": [
                {"ingredient": self.ingredient1.id, "quantity": 1},
                {"ingredient": self.ingredient2.id, "quantity": 2},
            ],
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Recipe.objects.count(), 1)
        recipe = Recipe.objects.first()
        self.assertEqual(recipe.name, "Test Recipe")

        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertTrue(
            IngredientRecipe.objects.filter(recipe=recipe, ingredient=self.ingredient1, ingredient_amount=1).exists()
        )
        self.assertTrue(
            IngredientRecipe.objects.filter(recipe=recipe, ingredient=self.ingredient2, ingredient_amount=2).exists()
        )

    def test_list_recipes(self):
        recipe = Recipe.objects.create(name="Test Recipe", description="Test description", user=self.user)
        IngredientRecipe.objects.create(recipe=recipe, ingredient=self.ingredient1, ingredient_amount=1)

        url = '/recipes/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], recipe.name)

    def test_list_recipes_with_ingredients(self):
        recipe = Recipe.objects.create(name="Test Recipe", description="Test description", user=self.user)
        IngredientRecipe.objects.create(recipe=recipe, ingredient=self.ingredient1, ingredient_amount=1)

        url = '/recipes/list_recipes_with_ingredients/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], recipe.name)
        self.assertEqual(response.data['data'][0]['ingredients'][0]['name'], self.ingredient1.name)
