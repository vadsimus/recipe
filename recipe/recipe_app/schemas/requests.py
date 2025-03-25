from pydantic import BaseModel, Field, condecimal, constr, conint
from typing import List


class IngredientInput(BaseModel):
    name: constr(max_length=100)
    cost: condecimal(max_digits=20, decimal_places=2)


class IngredientRecipeInput(BaseModel):
    ingredient_id: int
    ingredient_amount: conint(gt=0)


class RecipeInput(BaseModel):
    name: constr(max_length=200)
    description: str
    ingredients: List[IngredientRecipeInput] = Field(default_factory=list)


class UserRegistrationInput(BaseModel):
    username: constr(min_length=1)
    email: constr(min_length=1)
    password: constr(min_length=1)
