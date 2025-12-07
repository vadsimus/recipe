from typing import List
from decimal import Decimal
from recipe_app.models import IngredientRecipe, Recipe
from recipe_app.schemas.responses import RecipeResponse, RecipeIngredientResponse
from recipe_app.utils.common import round_decimal
from recipe_app.utils.unit_converter import (
    calculate_ingredient_price,
    convert_from_base_unit,
    get_base_unit,
    convert_to_base_unit
)


def build_recipe_response(recipe: Recipe, request) -> RecipeResponse:

    qs: List[IngredientRecipe] = recipe.ingredient_recipes.select_related('ingredient').all()

    ingredients_data = []
    for ir in qs:
        ingredient = ir.ingredient
        # Cost is already stored per base unit (e.g., cost per 1kg, 1L, or 1pcs)
        # cost_unit is always "1kg", "1l", or "1pcs" after conversion
        cost_per_base = Decimal(str(ingredient.cost))
        
        # Amount is stored in base unit (kg, L, or pcs)
        amount_in_base = Decimal(str(ir.ingredient_amount))
        
        # Calculate price: cost_per_base * amount_in_base
        # Since both are in base units, we can directly multiply
        price = cost_per_base * amount_in_base
        
        # Get display amount (convert from base if display_unit is specified)
        display_amount = amount_in_base
        display_unit = ir.display_unit or ingredient.unit
        
        if display_unit != get_base_unit(ingredient.unit):
            # Convert from base unit to display unit
            display_amount = convert_from_base_unit(amount_in_base, display_unit)
        
        ingredients_data.append(
            RecipeIngredientResponse(
                id=ingredient.id,
                name=ingredient.name,
                cost=ingredient.cost,
                unit=display_unit,  # Show display unit
                ingredient_amount=float(display_amount),  # Show converted amount
                ingredient_price=round_decimal(price),
            )
        )

    total = sum(i.ingredient_price for i in ingredients_data)
    return RecipeResponse(
        id=recipe.id,
        name=recipe.name,
        description=recipe.description,
        image=recipe.image.url if recipe.image else None,
        ingredients=ingredients_data,
        total_price=total,
    )
