import json
from decimal import Decimal

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .serializers import IngredientSerializer, RecipeSerializer, UserRegistrationSerializer
from .models import Recipe, Ingredient, IngredientRecipe


# Viewset for Recipe
class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    # Additional route to list recipes with ingredient details
    @action(detail=False, methods=['get'])
    def list_recipes_with_ingredients(self, request):
        recipes = Recipe.objects.all()
        data = []
        for recipe in recipes:
            ingredients_list = [
                {
                    'name': ir.ingredient.name,
                    'amount': ir.ingredient_amount,
                    'cost': ir.ingredient.cost
                }
                for ir in recipe.ingredientrecipe_set.all()
            ]
            data.append({
                'id': recipe.id,
                'name': recipe.name,
                'image_url': recipe.image_url,
                'description': recipe.description,
                'ingredients': ingredients_list
            })
        return Response({'result': 'ok', 'data': data}, status=status.HTTP_200_OK)


# Viewset for Ingredient
class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


# Function-based view to create an ingredient
@api_view(['POST'])
def create_ingredient(request):
    serializer = IngredientSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'result': 'ok'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# APIView to create a recipe with ingredients
class CreateRecipeView(APIView):

    def post(self, request, *args, **kwargs):
        data = request.data
        recipe_serializer = RecipeSerializer(data={
            'name': data.get('title'),
            'image_url': data.get('image_url'),
            'description': data.get('description')
        })

        if recipe_serializer.is_valid():
            recipe = recipe_serializer.save()
            ingredients = data.get('ingredients', [])
            for ingredient_data in ingredients:
                ingredient = Ingredient.objects.get(pk=ingredient_data['ingredient'])
                IngredientRecipe.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    ingredient_amount=ingredient_data['quantity']
                )
            return Response({'result': 'ok'}, status=status.HTTP_201_CREATED)
        return Response(recipe_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API to get all ingredients as JSON
@api_view(['GET'])
def get_ingredients(request):
    ingredients = Ingredient.objects.all()
    serializer = IngredientSerializer(ingredients, many=True)
    return Response({'result': 'ok', 'data': serializer.data}, status=status.HTTP_200_OK)


# API for user registration
@api_view(['POST'])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user_name = serializer.validated_data['username']
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': f"Email '{email}' is already in use."}, status=status.HTTP_400_BAD_REQUEST)
        User.objects.create_user(username=user_name, email=email, password=password)
        # User.save()
        return Response({'result': 'ok', 'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Both username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'result': 'ok', 'token': token.key},
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {'error': 'Invalid username or password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        request.user.auth_token.delete()
        return Response({'result': 'ok', 'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    except AttributeError:
        return Response({'error': 'User is not logged in.'}, status=status.HTTP_400_BAD_REQUEST)
