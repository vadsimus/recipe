from django.db import models
from django.contrib.auth.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    cost = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ingredients')

    class Meta:
        unique_together = ('name', 'user')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    image_url = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through='IngredientRecipe')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')

    class Meta:
        unique_together = ('name', 'user')

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredient_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredient_recipes')
    ingredient_amount = models.PositiveIntegerField()

    class Meta:
        unique_together = ('ingredient', 'recipe')

    def __str__(self):
        return f"{self.recipe.name} - {self.ingredient.name}"
