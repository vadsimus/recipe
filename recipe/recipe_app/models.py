from django.db import models
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


class Ingredient(models.Model):
    class Unit(models.TextChoices):
        LITER = 'l', 'liters'
        GRAM = 'g', 'grams'
        PIECE = 'pcs', 'pieces'

    class CostUnit(models.TextChoices):
        # Weight units
        KG_1 = '1kg', '1 kg'
        G_100 = '100g', '100 g'
        G_500 = '500g', '500 g'
        # Volume units
        L_1 = '1l', '1 L'
        ML_100 = '100ml', '100 ml'
        ML_500 = '500ml', '500 ml'
        # Piece units
        PCS_1 = '1pcs', '1 piece'
        PCS_10 = '10pcs', '10 pieces'

    name = models.CharField(max_length=100)
    cost = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ingredients')
    unit = models.CharField(max_length=3, choices=Unit.choices, default=Unit.GRAM)
    cost_unit = models.CharField(max_length=10, choices=CostUnit.choices, default=CostUnit.KG_1, 
                                  help_text='The unit for which the cost is specified')

    class Meta:
        unique_together = ('name', 'unit', 'user')

    def __str__(self):
        return self.name


def validate_image(image):
    max_size_mb = 5  # 5 MB
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Image size exceeds the allowed limit: {max_size_mb} MB")


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='recipes/', validators=[validate_image], null=True, blank=True)
    description = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through='IngredientRecipe')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')

    class Meta:
        unique_together = ('name', 'user')

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    class DisplayUnit(models.TextChoices):
        # Weight units
        KG = 'kg', 'kg'
        G = 'g', 'g'
        # Volume units
        L = 'l', 'L'
        ML = 'ml', 'ml'
        # Piece units
        PCS = 'pcs', 'pieces'

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredient_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredient_recipes')
    ingredient_amount = models.DecimalField(max_digits=10, decimal_places=6, 
                                            help_text='Amount stored in base unit (kg for weight, L for volume)')
    display_unit = models.CharField(max_length=5, choices=DisplayUnit.choices, null=True, blank=True,
                                   help_text='Unit to display/enter in recipe (optional, defaults to ingredient unit)')

    class Meta:
        unique_together = ('ingredient', 'recipe')

    def __str__(self):
        return f"{self.recipe.name} - {self.ingredient.name}"
