from typing import List
from recipe_app.models import IngredientRecipe, Recipe
from recipe_app.schemas.responses import RecipeResponse, RecipeIngredientResponse


def build_recipe_response(recipe: Recipe, request) -> RecipeResponse:

    qs: List[IngredientRecipe] = recipe.ingredient_recipes.select_related('ingredient').all()

    ingredients_data = []
    for ir in qs:
        cost = float(ir.ingredient.cost)
        amount = ir.ingredient_amount
        price = cost * amount
        ingredients_data.append(
            RecipeIngredientResponse(
                id=ir.ingredient.id,
                name=ir.ingredient.name,
                cost=ir.ingredient.cost,
                ingredient_amount=amount,
                ingredient_price=price,
            )
        )

    total = sum(i.ingredient_price for i in ingredients_data)
    return RecipeResponse(
        id=recipe.id,
        name=recipe.name,
        description=recipe.description,
        image=request.build_absolute_uri(recipe.image.url) if recipe.image else None,
        ingredients=ingredients_data,
        total_price=total,
    )
