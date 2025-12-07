from pydantic import BaseModel, Field, condecimal, constr, conint
from typing import List, Literal, Optional


class IngredientInput(BaseModel):
    name: constr(max_length=100)
    cost: condecimal(max_digits=20, decimal_places=2)
    unit: Literal['g', 'l', 'pcs'] = 'g'
    cost_unit: Literal['1kg', '100g', '500g', '1l', '100ml', '500ml', '1pcs', '10pcs'] = '1kg'


class IngredientRecipeInput(BaseModel):
    ingredient_id: int
    ingredient_amount: condecimal(max_digits=10, decimal_places=6, gt=0)
    display_unit: Optional[Literal['kg', 'g', 'l', 'ml', 'pcs']] = None


class RecipeInput(BaseModel):
    name: constr(max_length=200)
    description: str
    ingredients: List[IngredientRecipeInput] = Field(default_factory=list)


class UserRegistrationInput(BaseModel):
    username: constr(min_length=1)
    email: constr(min_length=1)
    password: constr(min_length=1)
