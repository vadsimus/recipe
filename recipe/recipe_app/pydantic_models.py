from pydantic import BaseModel, Field, HttpUrl, conint, constr, condecimal
from typing import List, Optional


# Pydantic model for Ingredient input data
class IngredientInput(BaseModel):
    name: constr(max_length=100)
    cost: condecimal(max_digits=20, decimal_places=2)


# Pydantic model for Ingredient output data
class IngredientOutput(IngredientInput):
    id: int


# Pydantic model for nested IngredientRecipe input data (for recipes)
class IngredientRecipeInput(BaseModel):
    ingredient_id: int
    ingredient_amount: conint(gt=0)  # Must be a positive integer


# Pydantic model for nested IngredientRecipe output data (for recipes)
class IngredientRecipeOutput(BaseModel):
    ingredient: IngredientOutput
    ingredient_amount: int


# Pydantic model for Recipe input data
class RecipeInput(BaseModel):
    name: constr(max_length=200)
    description: str
    # Image is handled separately via file upload endpoint.
    ingredients: List[IngredientRecipeInput] = Field(default_factory=list)


# Pydantic model for Recipe output data
class RecipeOutput(BaseModel):
    id: int
    name: str
    description: str
    image: Optional[HttpUrl] = None
    ingredients: List[IngredientRecipeOutput] = Field(default_factory=list)


# Pydantic model for User registration input data
class UserRegistrationInput(BaseModel):
    username: constr(min_length=1)
    email: constr(min_length=1)
    password: constr(min_length=1)
