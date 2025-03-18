from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Any

from recipe_app.schemas.requests import IngredientInput


class IngredientOutput(IngredientInput):
    id: int


class IngredientRecipeOutput(BaseModel):
    ingredient: IngredientOutput
    ingredient_amount: int


class RecipeOutput(BaseModel):
    id: int
    name: str
    description: str
    image: Optional[HttpUrl] = None
    ingredients: List[IngredientRecipeOutput] = Field(default_factory=list)


class APIResponse(BaseModel):
    result: str
    data: Any = None
    message: Optional[str] = None
