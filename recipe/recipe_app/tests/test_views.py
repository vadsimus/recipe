from io import BytesIO
from PIL import Image
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from recipe_app.models import Ingredient, Recipe, IngredientRecipe


def generate_image():
    file = BytesIO()
    image = Image.new('RGB', (100, 100), 'white')
    image.save(file, 'jpeg')
    file.name = 'test.jpg'
    file.seek(0)
    return file


class RecipeAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

        self.ingredient1 = Ingredient.objects.create(name="Salt", cost=0.5, user=self.user)
        self.ingredient2 = Ingredient.objects.create(name="Sugar", cost=1.0, user=self.user)

    def test_create_recipe_with_ingredients(self):
        url = '/api/recipes/'
        data = {
            "name": "Test Recipe",
            "description": "Test description",
            "ingredients": [
                {"ingredient_id": self.ingredient1.id, "ingredient_amount": 1},
                {"ingredient_id": self.ingredient2.id, "ingredient_amount": 2},
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

        url = '/api/recipes/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data.get('data')), 1)
        self.assertEqual(response.data.get('data')[0]['name'], recipe.name)

    def test_list_recipes_with_ingredients(self):
        recipe = Recipe.objects.create(name="Test Recipe", description="Test description", user=self.user)
        IngredientRecipe.objects.create(recipe=recipe, ingredient=self.ingredient1, ingredient_amount=1)

        url = '/api/recipes/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], recipe.name)
        self.assertEqual(response.data['data'][0]['ingredients'][0]['ingredient']['name'], self.ingredient1.name)

    def test_upload_image(self):
        recipe = Recipe.objects.create(name="Test Recipe", description="Test description", user=self.user)

        url = f'/api/recipes/{recipe.id}/upload-image/'
        image = generate_image()
        response = self.client.post(url, {'image': image}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        self.assertTrue(bool(recipe.image))

    def test_create_recipe_with_invalid_ingredient(self):
        url = '/api/recipes/'
        data = {
            "name": "Test Recipe",
            "description": "Test description",
            "ingredients": [
                {"ingredient_id": 999, "ingredient_amount": 1},
            ],
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response.data.get("result"), "error")
        self.assertIsNone(response.data.get("data"))

        expected_error = 'Invalid pk "999" - object does not exist.'
        self.assertEqual(response.data.get("message"), expected_error)

    def test_recipes_filtered_by_user(self):
        user_recipe = Recipe.objects.create(name="User Recipe", description="User description", user=self.user)

        url = '/api/recipes/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data.get('data')), 1)
        self.assertEqual(response.data.get('data')[0]['name'], user_recipe.name)
