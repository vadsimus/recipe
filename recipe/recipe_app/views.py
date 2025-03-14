from typing import Any
from django.db import transaction
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema

from .models import Ingredient, Recipe, IngredientRecipe
from .pydantic_models import (
    IngredientInput,
    IngredientOutput,
    RecipeInput,
    RecipeOutput,
    IngredientRecipeOutput,
    UserRegistrationInput,
)
from .pydantic_base_view import PydanticAPIView, FileUploadPydanticAPIView
from pydantic import BaseModel

# Для удобства определим константу ref_template,
# чтобы использовать её во всех вызовах .model_json_schema()
REF_TEMPLATE = '#/components/schemas/{model}'


# -------------------------------
# IngredientListCreateView
# -------------------------------
class IngredientListCreateView(PydanticAPIView):
    permission_classes = [IsAuthenticated]
    pydantic_model = IngredientInput  # Для POST валидации

    @extend_schema(
        responses={
            200: {
                "type": "object",
                "properties": {
                    "result": {"type": "string"},
                    "data": {"type": "array", "items": IngredientOutput.model_json_schema(ref_template=REF_TEMPLATE)},
                },
            }
        }
    )
    def get(self, request, *args, **kwargs):
        ingredients = Ingredient.objects.filter(user=request.user)
        output = [IngredientOutput(id=i.id, name=i.name, cost=i.cost).model_dump(mode='json') for i in ingredients]
        return Response({"result": "ok", "data": output})

    @extend_schema(
        request=IngredientInput.model_json_schema(ref_template=REF_TEMPLATE),
        responses={
            201: {
                "type": "object",
                "properties": {
                    "result": {"type": "string"},
                    "data": IngredientOutput.model_json_schema(ref_template=REF_TEMPLATE),
                },
            }
        },
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.pydantic.model_dump(mode='json')
        ingredient = Ingredient.objects.create(user=request.user, **data)
        output = IngredientOutput(id=ingredient.id, name=ingredient.name, cost=ingredient.cost).model_dump(mode='json')
        return Response({"result": "ok", "data": output}, status=status.HTTP_201_CREATED)


# -------------------------------
# RecipeListCreateView
# -------------------------------
class RecipeListCreateView(PydanticAPIView):
    permission_classes = [IsAuthenticated]
    pydantic_model = RecipeInput

    @extend_schema(
        responses={
            200: {
                "type": "object",
                "properties": {
                    "result": {"type": "string"},
                    "data": {"type": "array", "items": RecipeOutput.model_json_schema(ref_template=REF_TEMPLATE)},
                },
            }
        }
    )
    def get(self, request, *args, **kwargs):
        recipes = Recipe.objects.filter(user=request.user)
        output = []
        for recipe in recipes:
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
        return Response({"result": "ok", "data": output})

    @extend_schema(
        request=RecipeInput.model_json_schema(ref_template=REF_TEMPLATE),
        responses={
            201: {
                "type": "object",
                "properties": {
                    "result": {"type": "string"},
                    "data": RecipeOutput.model_json_schema(ref_template=REF_TEMPLATE),
                },
            }
        },
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.pydantic.model_dump(mode='json')
        recipe = Recipe.objects.create(name=data['name'], description=data['description'], user=request.user)
        for ingr_data in data.get('ingredients', []):
            ingredient = Ingredient.objects.filter(id=ingr_data['ingredient_id'], user=request.user).first()
            if not ingredient:
                return Response(
                    {
                        "ingredients": [
                            {"ingredient": [f'Invalid pk "{ingr_data["ingredient_id"]}" - object does not exist.']}
                        ]
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
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
        return Response({"result": "ok", "data": output}, status=status.HTTP_201_CREATED)


# -------------------------------
# RecipeDetailView
# -------------------------------
class RecipeDetailView(PydanticAPIView):
    permission_classes = [IsAuthenticated]
    pydantic_model = RecipeInput

    def get_object(self, pk):
        return get_object_or_404(Recipe, pk=pk, user=self.request.user)

    @extend_schema(
        responses={
            200: {
                "type": "object",
                "properties": {
                    "result": {"type": "string"},
                    "data": RecipeOutput.model_json_schema(ref_template=REF_TEMPLATE),
                },
            }
        }
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
        return Response({"result": "ok", "data": output})

    @extend_schema(
        request=RecipeInput.model_json_schema(ref_template=REF_TEMPLATE),
        responses={
            200: {
                "type": "object",
                "properties": {
                    "result": {"type": "string"},
                    "data": RecipeOutput.model_json_schema(ref_template=REF_TEMPLATE),
                },
            }
        },
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
        return Response({"result": "ok", "data": output})

    @extend_schema(
        request=RecipeInput.model_json_schema(ref_template=REF_TEMPLATE),
        responses={
            200: {
                "type": "object",
                "properties": {
                    "result": {"type": "string"},
                    "data": RecipeOutput.model_json_schema(ref_template=REF_TEMPLATE),
                },
            }
        },
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
            ingredients_output.append(
                IngredientRecipeOutput(
                    ingredient=IngredientOutput(id=ir.ingredient.id, name=ir.ingredient.name, cost=ir.ingredient.cost),
                    ingredient_amount=ir.ingredient_amount,
                ).model_dump(mode='json')
            )
        output = RecipeOutput(
            id=recipe.id,
            name=recipe.name,
            description=recipe.description,
            image=request.build_absolute_uri(recipe.image.url) if recipe.image else None,
            ingredients=ingredients_output,
        ).model_dump(mode='json')
        return Response({"result": "ok", "data": output})


# -------------------------------
# RecipeImageUploadView
# -------------------------------
class RecipeImageUploadView(FileUploadPydanticAPIView):
    permission_classes = [IsAuthenticated]
    file_fields = ['image']

    class FileUploadModel(BaseModel):
        image: Any = None
        model_config = {"extra": "allow"}

    pydantic_model = FileUploadModel

    @extend_schema(
        request=FileUploadModel.model_json_schema(ref_template=REF_TEMPLATE),
        responses={
            200: {
                "type": "object",
                "properties": {
                    "result": {"type": "string"},
                    "message": {"type": "string"},
                    "data": RecipeOutput.model_json_schema(ref_template=REF_TEMPLATE),
                },
            },
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
    )
    def post(self, request, pk, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=pk, user=request.user)
        image = request.FILES.get('image')
        if not image:
            return Response({"error": "Image not uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if image.content_type not in allowed_types:
            return Response(
                {"error": "Unsupported image format. Allowed: JPEG, PNG, GIF."}, status=status.HTTP_400_BAD_REQUEST
            )
        max_size = 5 * 1024 * 1024  # 5 MB
        if image.size > max_size:
            return Response(
                {"error": "Image size exceeds the allowed limit (5 MB)."}, status=status.HTTP_400_BAD_REQUEST
            )
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
            {"result": "ok", "message": "Image successfully uploaded", "data": output}, status=status.HTTP_200_OK
        )


# -------------------------------
# UserRegistrationView
# -------------------------------
class UserRegistrationView(PydanticAPIView):
    permission_classes = [AllowAny]
    pydantic_model = UserRegistrationInput

    @extend_schema(
        request=UserRegistrationInput.model_json_schema(ref_template=REF_TEMPLATE),
        responses={
            201: {"type": "object", "properties": {"result": {"type": "string"}, "message": {"type": "string"}}},
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
    )
    def post(self, request, *args, **kwargs):
        data = request.pydantic.model_dump(mode='json')
        if User.objects.filter(username=data['username']).exists():
            return Response(
                {"error": f"Username '{data['username']}' is already taken."}, status=status.HTTP_400_BAD_REQUEST
            )
        if User.objects.filter(email=data['email']).exists():
            return Response(
                {"error": f"Email '{data['email']}' is already in use."}, status=status.HTTP_400_BAD_REQUEST
            )
        User.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
        return Response({"result": "ok", "message": "User successfully registered."}, status=status.HTTP_201_CREATED)
