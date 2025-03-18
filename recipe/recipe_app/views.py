from typing import Any, Optional
from django.db import transaction
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema

from .models import Ingredient, Recipe, IngredientRecipe
from recipe_app.schemas.requests import IngredientInput, RecipeInput, UserRegistrationInput
from recipe_app.schemas.responses import IngredientOutput, RecipeOutput, IngredientRecipeOutput, APIResponse
from .pydantic_base_view import PydanticAPIView, FileUploadPydanticAPIView
from .utils.pydantic_parameters import PydanticModelParameters
from pydantic import BaseModel


class IngredientFilter(BaseModel):
    name: Optional[str] = None


class RecipeFilter(BaseModel):
    name: Optional[str] = None


class IngredientListCreateView(PydanticAPIView):
    permission_classes = [IsAuthenticated]
    pydantic_model = IngredientInput  # Validate POST request body with IngredientInput

    @extend_schema(
        parameters=PydanticModelParameters(IngredientFilter).get_parameters(),
        responses={200: APIResponse},
        summary="List Ingredients",
        description="Fetch ingredients for the authenticated user with an optional filter by name.",
    )
    def get(self, request, *args, **kwargs):
        name = request.query_params.get('name')
        queryset = Ingredient.objects.filter(user=request.user)
        if name:
            queryset = queryset.filter(name__icontains=name)
        output = [IngredientOutput(id=i.id, name=i.name, cost=i.cost).model_dump(mode='json') for i in queryset]
        return Response(APIResponse(result="ok", data=output).model_dump(mode='json'))

    @extend_schema(
        request=IngredientInput,
        responses={201: APIResponse},
        summary="Create Ingredient",
        description="Creates a new ingredient for the authenticated user.",
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.pydantic.model_dump(mode='json')
        ingredient = Ingredient.objects.create(user=request.user, **data)
        output = IngredientOutput(id=ingredient.id, name=ingredient.name, cost=ingredient.cost).model_dump(mode='json')
        return Response(APIResponse(result="ok", data=output).model_dump(mode='json'), status=status.HTTP_201_CREATED)


class RecipeListCreateView(PydanticAPIView):
    permission_classes = [IsAuthenticated]
    pydantic_model = RecipeInput

    @extend_schema(
        parameters=PydanticModelParameters(RecipeFilter).get_parameters(),
        responses={200: APIResponse},
        summary="List Recipes",
        description="Fetch recipes for the authenticated user with an optional filter by name.",
    )
    def get(self, request, *args, **kwargs):
        name = request.query_params.get('name')
        queryset = Recipe.objects.filter(user=request.user)
        if name:
            queryset = queryset.filter(name__icontains=name)
        output = []
        for recipe in queryset:
            ingredients_output = []
            for ir in recipe.ingredient_recipes.all():
                ingr_out = IngredientRecipeOutput(
                    ingredient=IngredientOutput(id=ir.ingredient.id, name=ir.ingredient.name, cost=ir.ingredient.cost),
                    ingredient_amount=ir.ingredient_amount,
                ).model_dump(mode='json')
                ingredients_output.append(ingr_out)

            recipe_data = RecipeOutput(
                id=recipe.id,
                name=recipe.name,
                description=recipe.description,
                image=request.build_absolute_uri(recipe.image.url) if recipe.image else None,
                ingredients=ingredients_output,
            ).model_dump(mode='json')
            output.append(recipe_data)
        return Response(APIResponse(result="ok", data=output).model_dump(mode='json'))

    @extend_schema(
        request=RecipeInput,
        responses={201: APIResponse},
        summary="Create Recipe",
        description="Creates a new recipe for the authenticated user along with its ingredients.",
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.pydantic.model_dump(mode='json')
        recipe = Recipe.objects.create(name=data['name'], description=data['description'], user=request.user)
        for ingr_data in data.get('ingredients', []):
            ingredient = Ingredient.objects.filter(id=ingr_data['ingredient_id'], user=request.user).first()
            if not ingredient:
                error_response = APIResponse(
                    result="error", message=f'Invalid pk "{ingr_data["ingredient_id"]}" - object does not exist.'
                ).model_dump(mode='json')
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
            IngredientRecipe.objects.create(
                recipe=recipe, ingredient=ingredient, ingredient_amount=ingr_data['ingredient_amount']
            )
        ingredients_output = []
        for ir in recipe.ingredient_recipes.all():
            ingr_out = IngredientRecipeOutput(
                ingredient=IngredientOutput(id=ir.ingredient.id, name=ir.ingredient.name, cost=ir.ingredient.cost),
                ingredient_amount=ir.ingredient_amount,
            ).model_dump(mode='json')
            ingredients_output.append(ingr_out)
        output = RecipeOutput(
            id=recipe.id,
            name=recipe.name,
            description=recipe.description,
            image=request.build_absolute_uri(recipe.image.url) if recipe.image else None,
            ingredients=ingredients_output,
        ).model_dump(mode='json')
        return Response(APIResponse(result="ok", data=output).model_dump(mode='json'), status=status.HTTP_201_CREATED)


class RecipeDetailView(PydanticAPIView):
    permission_classes = [IsAuthenticated]
    pydantic_model = RecipeInput

    def get_object(self, pk):
        return get_object_or_404(Recipe, pk=pk, user=self.request.user)

    @extend_schema(
        responses={200: APIResponse},
        summary="Retrieve Recipe",
        description="Fetch the details of a specific recipe for the authenticated user.",
    )
    def get(self, request, pk, *args, **kwargs):
        recipe = self.get_object(pk)
        ingredients_output = []
        for ir in recipe.ingredient_recipes.all():
            ingr_out = IngredientRecipeOutput(
                ingredient=IngredientOutput(id=ir.ingredient.id, name=ir.ingredient.name, cost=ir.ingredient.cost),
                ingredient_amount=ir.ingredient_amount,
            ).model_dump(mode='json')
            ingredients_output.append(ingr_out)
        output = RecipeOutput(
            id=recipe.id,
            name=recipe.name,
            description=recipe.description,
            image=request.build_absolute_uri(recipe.image.url) if recipe.image else None,
            ingredients=ingredients_output,
        ).model_dump(mode='json')
        return Response(APIResponse(result="ok", data=output).model_dump(mode='json'))

    @extend_schema(
        request=RecipeInput,
        responses={200: APIResponse},
        summary="Update Recipe",
        description="Updates the details of a specific recipe for the authenticated user.",
    )
    @transaction.atomic
    def put(self, request, pk, *args, **kwargs):
        recipe = self.get_object(pk)
        data = request.pydantic.model_dump(mode='json')
        recipe.name = data['name']
        recipe.description = data['description']
        recipe.save()
        recipe.ingredient_recipes.all().delete()
        for ingr_data in data.get('ingredients', []):
            ingredient = get_object_or_404(Ingredient, id=ingr_data['ingredient_id'], user=request.user)
            IngredientRecipe.objects.create(
                recipe=recipe, ingredient=ingredient, ingredient_amount=ingr_data['ingredient_amount']
            )
        ingredients_output = []
        for ir in recipe.ingredient_recipes.all():
            ingr_out = IngredientRecipeOutput(
                ingredient=IngredientOutput(id=ir.ingredient.id, name=ir.ingredient.name, cost=ir.ingredient.cost),
                ingredient_amount=ir.ingredient_amount,
            ).model_dump(mode='json')
            ingredients_output.append(ingr_out)
        output = RecipeOutput(
            id=recipe.id,
            name=recipe.name,
            description=recipe.description,
            image=request.build_absolute_uri(recipe.image.url) if recipe.image else None,
            ingredients=ingredients_output,
        ).model_dump(mode='json')
        return Response(APIResponse(result="ok", data=output).model_dump(mode='json'))

    @extend_schema(
        request=RecipeInput,
        responses={200: APIResponse},
        summary="Partial Update Recipe",
        description="Updates selected fields of a specific recipe for the authenticated user.",
    )
    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        recipe = self.get_object(pk)
        partial_data = request.pydantic.model_dump(mode='json')
        if "name" in partial_data:
            recipe.name = partial_data["name"]
        if "description" in partial_data:
            recipe.description = partial_data["description"]
        recipe.save()
        if "ingredients" in partial_data:
            recipe.ingredient_recipes.all().delete()
            for ingr_data in partial_data.get("ingredients", []):
                ingredient = get_object_or_404(Ingredient, id=ingr_data["ingredient_id"], user=request.user)
                IngredientRecipe.objects.create(
                    recipe=recipe, ingredient=ingredient, ingredient_amount=ingr_data["ingredient_amount"]
                )
        ingredients_output = []
        for ir in recipe.ingredient_recipes.all():
            ingr_out = IngredientRecipeOutput(
                ingredient=IngredientOutput(id=ir.ingredient.id, name=ir.ingredient.name, cost=ir.ingredient.cost),
                ingredient_amount=ir.ingredient_amount,
            ).model_dump(mode='json')
            ingredients_output.append(ingr_out)
        output = RecipeOutput(
            id=recipe.id,
            name=recipe.name,
            description=recipe.description,
            image=request.build_absolute_uri(recipe.image.url) if recipe.image else None,
            ingredients=ingredients_output,
        ).model_dump(mode='json')
        return Response(APIResponse(result="ok", data=output).model_dump(mode='json'))


class RecipeImageUploadView(FileUploadPydanticAPIView):
    permission_classes = [IsAuthenticated]
    file_fields = ['image']

    class FileUploadModel(BaseModel):
        image: Any = None
        model_config = {"extra": "allow"}

    pydantic_model = FileUploadModel

    @extend_schema(
        request=FileUploadModel,
        responses={
            200: APIResponse,
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        summary="Upload Recipe Image",
        description="Uploads an image for a specific recipe and returns updated recipe data.",
    )
    def post(self, request, pk, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=pk, user=request.user)
        image = request.FILES.get('image')
        if not image:
            error_resp = APIResponse(result="error", message="Image not uploaded.").model_dump(mode='json')
            return Response(error_resp, status=status.HTTP_400_BAD_REQUEST)
        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if image.content_type not in allowed_types:
            error_resp = APIResponse(
                result="error", message="Unsupported image format. Allowed: JPEG, PNG, GIF."
            ).model_dump(mode='json')
            return Response(error_resp, status=status.HTTP_400_BAD_REQUEST)
        max_size = 5 * 1024 * 1024
        if image.size > max_size:
            error_resp = APIResponse(result="error", message="Image size exceeds the allowed limit (5 MB).").model_dump(
                mode='json'
            )
            return Response(error_resp, status=status.HTTP_400_BAD_REQUEST)
        recipe.image = image
        recipe.save()
        ingredients_output = []
        for ir in recipe.ingredient_recipes.all():
            ingr_out = IngredientRecipeOutput(
                ingredient=IngredientOutput(id=ir.ingredient.id, name=ir.ingredient.name, cost=ir.ingredient.cost),
                ingredient_amount=ir.ingredient_amount,
            ).model_dump(mode='json')
            ingredients_output.append(ingr_out)
        output = RecipeOutput(
            id=recipe.id,
            name=recipe.name,
            description=recipe.description,
            image=request.build_absolute_uri(recipe.image.url),
            ingredients=ingredients_output,
        ).model_dump(mode='json')
        return Response(
            APIResponse(result="ok", message="Image successfully uploaded", data=output).model_dump(mode='json'),
            status=status.HTTP_200_OK,
        )


class UserRegistrationView(PydanticAPIView):
    permission_classes = [AllowAny]
    pydantic_model = UserRegistrationInput

    @extend_schema(
        request=UserRegistrationInput,
        responses={
            201: {"type": "object", "properties": {"result": {"type": "string"}, "message": {"type": "string"}}},
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        summary="User Registration",
        description="Registers a new user with the provided username, email, and password.",
    )
    def post(self, request, *args, **kwargs):
        data = request.pydantic.model_dump(mode='json')
        if User.objects.filter(username=data['username']).exists():
            error_resp = APIResponse(
                result="error", message=f"Username '{data['username']}' is already taken."
            ).model_dump(mode='json')
            return Response(error_resp, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=data['email']).exists():
            error_resp = APIResponse(result="error", message=f"Email '{data['email']}' is already in use.").model_dump(
                mode='json'
            )
            return Response(error_resp, status=status.HTTP_400_BAD_REQUEST)
        User.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
        return Response(
            APIResponse(result="ok", message="User successfully registered.").model_dump(mode='json'),
            status=status.HTTP_201_CREATED,
        )
