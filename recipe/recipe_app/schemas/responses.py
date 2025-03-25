from typing import List, Optional, Any
from pydantic import BaseModel, condecimal, HttpUrl


class APIResponse(BaseModel):
    result: str
    message: Optional[str] = None
    data: Any = None


class IngredientResponse(BaseModel):
    id: int
    name: str
    cost: condecimal(max_digits=20, decimal_places=2)


class IngredientListResponse(APIResponse):
    data: List[IngredientResponse]


class IngredientCreateResponse(APIResponse):
    data: IngredientResponse


class RecipeResponse(BaseModel):
    id: int
    name: str
    description: str
    image: Optional[HttpUrl] = None
    ingredients: List[IngredientResponse]


class RecipeListResponse(APIResponse):
    data: List[RecipeResponse]


class RecipeCreateResponse(APIResponse):
    data: RecipeResponse


class RecipeDetailResponse(APIResponse):
    data: RecipeResponse


class RecipeUpdateResponse(APIResponse):
    data: RecipeResponse


class RecipePartialUpdateResponse(APIResponse):
    data: RecipeResponse


class RecipeImageUploadResponse(APIResponse):
    message: str
    data: RecipeResponse


class UserRegistrationResponse(APIResponse):
    message: str
