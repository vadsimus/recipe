from typing import Any

from django.db import transaction
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from pydantic import BaseModel

from .models import Ingredient, Recipe, IngredientRecipe
from recipe_app.schemas.requests import IngredientInput, RecipeInput, UserRegistrationInput
from recipe_app.schemas.responses import (
    APIResponse,
    IngredientResponse,
    IngredientListResponse,
    IngredientCreateResponse,
    RecipeListResponse,
    RecipeCreateResponse,
    RecipeDetailResponse,
    RecipeUpdateResponse,
    RecipePartialUpdateResponse,
    RecipeImageUploadResponse,
    UserRegistrationResponse,
)
from .pydantic_base_view import PydanticAPIView, FileUploadPydanticAPIView
from .utils.pydantic_parameters import PydanticModelParameters
from .utils.response_builders import build_recipe_response
from pydantic import ValidationError


class IngredientListCreateView(PydanticAPIView):
    permission_classes = [IsAuthenticated]
    pydantic_model = IngredientInput

    @extend_schema(
        responses={200: IngredientListResponse},
        summary="List Ingredients",
        description="Fetch ingredients for the authenticated user with an optional filter by name.",
    )
    def get(self, request, *args, **kwargs):
        name = request.query_params.get("name")
        queryset = Ingredient.objects.filter(user=request.user)
        if name:
            queryset = queryset.filter(name__icontains=name)
        output = [IngredientResponse(id=i.id, name=i.name, cost=i.cost, unit=i.unit) for i in queryset]
        response_data = IngredientListResponse(result="ok", data=output)
        return Response(response_data.model_dump(mode="json"))

    @extend_schema(
        request=IngredientInput,
        responses={201: IngredientCreateResponse},
        summary="Create Ingredient",
        description="Creates a new ingredient for the authenticated user.",
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.pydantic.model_dump(mode="json")
        ingredient = Ingredient.objects.create(user=request.user, **data)
        output = IngredientResponse(id=ingredient.id, name=ingredient.name, cost=ingredient.cost, unit=ingredient.unit)
        response_data = IngredientCreateResponse(result="ok", data=output)
        return Response(response_data.model_dump(mode="json"), status=status.HTTP_201_CREATED)


class IngredientDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Delete Ingredient",
        description="Delete an ingredient by ID if it belongs to the current user. Returns 204 on success.",
        responses={
            204: OpenApiResponse(description="Ingredient deleted successfully"),
            404: OpenApiResponse(description="Not found or does not belong to user"),
        },
    )
    def delete(self, request, pk, *args, **kwargs):
        ingredient = get_object_or_404(Ingredient, pk=pk, user=request.user)
        ingredient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Update Ingredient",
        description="Update an ingredient by ID if it belongs to the current user. Returns the updated ingredient.",
        request=IngredientInput,
        responses={
            200: IngredientResponse,
            400: OpenApiResponse(description="Wrong data format or validation error"),
            404: OpenApiResponse(description="Not found or does not belong to user"),
        },
    )
    def put(self, request, pk, *args, **kwargs):
        ingredient = get_object_or_404(Ingredient, pk=pk, user=request.user)

        try:
            validated = IngredientInput(**request.data)
        except ValidationError as e:
            return Response({'error': e.errors()}, status=status.HTTP_400_BAD_REQUEST)

        ingredient.name = validated.name
        ingredient.cost = validated.cost
        ingredient.unit = validated.unit
        ingredient.save()

        response = IngredientResponse(
            id=ingredient.id, name=ingredient.name, cost=ingredient.cost, unit=ingredient.unit
        )
        return Response(response.model_dump(mode="json"), status=status.HTTP_200_OK)


class RecipeListCreateView(PydanticAPIView):
    permission_classes = [IsAuthenticated]
    pydantic_model = RecipeInput

    @extend_schema(
        parameters=PydanticModelParameters(RecipeInput).get_parameters(),
        responses={200: RecipeListResponse},
        summary="List Recipes",
        description="Fetch recipes for the authenticated user with an optional filter by name.",
    )
    def get(self, request, *args, **kwargs):
        name = request.query_params.get("name")
        queryset = Recipe.objects.filter(user=request.user).prefetch_related("ingredient_recipes__ingredient")
        if name:
            queryset = queryset.filter(name__icontains=name)
        output = [build_recipe_response(recipe, request) for recipe in queryset]
        response_data = RecipeListResponse(result="ok", data=output)
        return Response(response_data.model_dump(mode="json"))

    @extend_schema(
        request=RecipeInput,
        responses={201: RecipeCreateResponse},
        summary="Create Recipe",
        description="Creates a new recipe for the authenticated user along with its ingredients.",
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.pydantic.model_dump(mode="json")
        recipe = Recipe.objects.create(
            name=data["name"],
            description=data["description"],
            user=request.user,
        )
        for ingr_data in data.get("ingredients", []):
            ingredient = Ingredient.objects.filter(id=ingr_data["ingredient_id"], user=request.user).first()
            if not ingredient:
                error_response = APIResponse(
                    result="error",
                    message=f'Invalid pk "{ingr_data["ingredient_id"]}" - object does not exist.',
                )
                return Response(error_response.model_dump(mode="json"), status=status.HTTP_400_BAD_REQUEST)
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                ingredient_amount=ingr_data["ingredient_amount"],
            )
        output = build_recipe_response(recipe, request)
        response_data = RecipeCreateResponse(result="ok", data=output)
        return Response(response_data.model_dump(mode="json"), status=status.HTTP_201_CREATED)


class RecipeDetailView(PydanticAPIView):
    permission_classes = [IsAuthenticated]
    pydantic_model = RecipeInput

    def get_object(self, pk):
        return get_object_or_404(Recipe, pk=pk, user=self.request.user)

    @extend_schema(
        responses={200: RecipeDetailResponse},
        summary="Retrieve Recipe",
        description="Fetch the details of a specific recipe for the authenticated user.",
    )
    def get(self, request, pk, *args, **kwargs):
        recipe = self.get_object(pk)
        output = build_recipe_response(recipe, request)
        response_data = RecipeDetailResponse(result="ok", data=output)
        return Response(response_data.model_dump(mode="json"))

    @extend_schema(
        request=RecipeInput,
        responses={200: RecipeUpdateResponse},
        summary="Update Recipe",
        description="Updates the details of a specific recipe for the authenticated user.",
    )
    @transaction.atomic
    def put(self, request, pk, *args, **kwargs):
        recipe = self.get_object(pk)
        data = request.pydantic.model_dump(mode="json")
        recipe.name = data["name"]
        recipe.description = data["description"]
        recipe.save()
        recipe.ingredient_recipes.all().delete()
        for ingr_data in data.get("ingredients", []):
            ingredient = get_object_or_404(Ingredient, id=ingr_data["ingredient_id"], user=request.user)
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                ingredient_amount=ingr_data["ingredient_amount"],
            )
        output = build_recipe_response(recipe, request)
        response_data = RecipeUpdateResponse(result="ok", data=output)
        return Response(response_data.model_dump(mode="json"))

    @extend_schema(
        request=RecipeInput,
        responses={200: RecipePartialUpdateResponse},
        summary="Partial Update Recipe",
        description="Updates selected fields of a specific recipe for the authenticated user.",
    )
    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        recipe = self.get_object(pk)
        partial_data = request.pydantic.model_dump(mode="json")
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
                    recipe=recipe,
                    ingredient=ingredient,
                    ingredient_amount=ingr_data["ingredient_amount"],
                )
        output = build_recipe_response(recipe, request)
        response_data = RecipePartialUpdateResponse(result="ok", data=output)
        return Response(response_data.model_dump(mode="json"))

    @extend_schema(
        responses={204: None},
        summary="Delete Recipe",
        description="Deletes a specific recipe for the authenticated user.",
    )
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        recipe = self.get_object(pk)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeImageUploadView(FileUploadPydanticAPIView):
    permission_classes = [IsAuthenticated]
    file_fields = ["image"]

    class FileUploadModel(BaseModel):
        image: Any = None
        model_config = {"extra": "allow"}

    pydantic_model = FileUploadModel

    @extend_schema(
        request=FileUploadModel,
        responses={
            200: RecipeImageUploadResponse,
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        summary="Upload Recipe Image",
        description="Uploads an image for a specific recipe and returns updated recipe data.",
    )
    def post(self, request, pk, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=pk, user=request.user)
        image = request.FILES.get("image")
        if not image:
            error_resp = APIResponse(result="error", message="Image not uploaded.")
            return Response(error_resp.model_dump(mode="json"), status=status.HTTP_400_BAD_REQUEST)
        allowed_types = ["image/jpeg", "image/png", "image/gif"]
        if image.content_type not in allowed_types:
            error_resp = APIResponse(result="error", message="Unsupported image format. Allowed: JPEG, PNG, GIF.")
            return Response(error_resp.model_dump(mode="json"), status=status.HTTP_400_BAD_REQUEST)
        max_size = 5 * 1024 * 1024
        if image.size > max_size:
            error_resp = APIResponse(result="error", message="Image size exceeds the allowed limit (5 MB).")
            return Response(error_resp.model_dump(mode="json"), status=status.HTTP_400_BAD_REQUEST)
        recipe.image = image
        recipe.save()
        output = build_recipe_response(recipe, request)
        response_data = RecipeImageUploadResponse(result="ok", message="Image successfully uploaded", data=output)
        return Response(response_data.model_dump(mode="json"), status=status.HTTP_200_OK)


class UserRegistrationView(PydanticAPIView):
    permission_classes = [AllowAny]
    pydantic_model = UserRegistrationInput

    @extend_schema(
        request=UserRegistrationInput,
        responses={
            201: UserRegistrationResponse,
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        summary="User Registration",
        description="Registers a new user with the provided username, email, and password.",
    )
    def post(self, request, *args, **kwargs):
        data = request.pydantic.model_dump(mode="json")
        if User.objects.filter(username=data['username']).exists():
            error_resp = APIResponse(result="error", message=f"Username '{data['username']}' is already taken.")
            return Response(error_resp.model_dump(mode="json"), status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=data['email']).exists():
            error_resp = APIResponse(result="error", message=f"Email '{data['email']}' is already in use.")
            return Response(error_resp.model_dump(mode="json"), status=status.HTTP_400_BAD_REQUEST)
        User.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
        response_data = UserRegistrationResponse(result="ok", message="User successfully registered.")
        return Response(response_data.model_dump(mode="json"), status=status.HTTP_201_CREATED)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]  # Require authentication

    def get(self, request):
        # user = request.user
        return Response(
            {
                'success': True,
                'data': {
                    'name': 'Serati Man',
                    'avatar': 'https://gw.alipayobjects.com/zos/antfincdn/XAosXuNZyF/BiazfanxmamNRoxxVxka.png',
                    'userid': '00000001',
                    'email': 'antdesign@alipay.com',
                    'signature': '海纳百川，有容乃大',
                    'title': '交互专家',
                    'group': '蚂蚁金服－某某某事业群－某某平台部－某某技术部－UED',
                    'tags': [
                        {
                            'key': '0',
                            'label': '很有想法的',
                        },
                    ],
                    'notifyCount': 12,
                    'unreadCount': 11,
                    'country': 'China',
                    'access': 'admin',
                    'geographic': {
                        'province': {
                            'label': '浙江省',
                            'key': '330000',
                        },
                        'city': {
                            'label': '杭州市',
                            'key': '330100',
                        },
                    },
                    'address': '西湖区工专路 77 号',
                    'phone': '0752-268888888',
                },
            }
        )
