from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .serializers import IngredientSerializer, RecipeSerializer, UserRegistrationSerializer
from .models import Recipe, Ingredient, IngredientRecipe


# Viewset for Recipe
class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        recipe = serializer.save(user=self.request.user)

        ingredients_data = self.request.data.get('ingredients', [])
        for ingredient_data in ingredients_data:
            try:
                ingredient = Ingredient.objects.get(pk=ingredient_data['ingredient'], user=self.request.user)
            except Ingredient.DoesNotExist:
                raise ValidationError(
                    {
                        'ingredient': f"Ingredient with id {ingredient_data['ingredient']} does not exist or does not belong to the user."
                    }
                )

            IngredientRecipe.objects.create(
                recipe=recipe, ingredient=ingredient, ingredient_amount=ingredient_data['quantity']
            )

    # Additional route to list recipes with ingredient details
    @action(detail=False, methods=['get'])
    def list_recipes_with_ingredients(self, request):
        recipes = self.get_queryset().prefetch_related('ingredient_recipes__ingredient')

        data = []
        for recipe in recipes:
            ingredients_list = [
                {
                    'name': ingredient_recipe.ingredient.name,
                    'amount': ingredient_recipe.ingredient_amount,
                    'cost': ingredient_recipe.ingredient.cost,
                }
                for ingredient_recipe in recipe.ingredient_recipes.all()
            ]
            data.append(
                {
                    'id': recipe.id,
                    'name': recipe.name,
                    'image': request.build_absolute_uri(recipe.image.url) if recipe.image else None,
                    'description': recipe.description,
                    'ingredients': ingredients_list,
                }
            )

        return Response({'result': 'ok', 'data': data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='upload-image')
    def upload_image(self, request, pk=None):
        # Кастомный эндпоинт для загрузки/обновления изображения
        recipe = self.get_object()
        image = request.FILES.get('image')

        if not image:
            return Response({'error': 'Изображение не загружено'}, status=status.HTTP_400_BAD_REQUEST)

        recipe.image = image
        recipe.save()

        return Response({'message': 'Изображение успешно загружено'}, status=status.HTTP_200_OK)


# Viewset for Ingredient
class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ingredient.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Function-based view to create an ingredient
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_ingredient(request):
    serializer = IngredientSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({'result': 'ok'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# APIView to create a recipe with ingredients
class CreateRecipeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data

        recipe_serializer = RecipeSerializer(
            data={'name': data.get('title'), 'image_url': data.get('image_url'), 'description': data.get('description')}
        )

        if recipe_serializer.is_valid():
            recipe = recipe_serializer.save(user=request.user)

            ingredients = data.get('ingredients', [])
            for ingredient_data in ingredients:
                try:
                    ingredient = Ingredient.objects.get(pk=ingredient_data['ingredient'], user=request.user)
                except Ingredient.DoesNotExist:
                    return Response(
                        {
                            'error': f"Ingredient with id {ingredient_data['ingredient']} does not exist or does not belong to the user."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                IngredientRecipe.objects.create(
                    recipe=recipe, ingredient=ingredient, ingredient_amount=ingredient_data['quantity']
                )

            return Response({'result': 'ok', 'recipe_id': recipe.id}, status=status.HTTP_201_CREATED)

        return Response(recipe_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API to get all ingredients as JSON
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ingredients(request):
    ingredients = Ingredient.objects.filter(user=request.user)
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
            return Response({'error': f"Email '{email}' is already in use."}, status=status.HTTP_400_BAD_REQUEST)
        User.objects.create_user(username=user_name, email=email, password=password)
        # User.save()
        return Response({'result': 'ok', 'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Both username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'result': 'ok', 'token': token.key}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        request.user.auth_token.delete()
        return Response({'result': 'ok', 'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    except AttributeError:
        return Response({'error': 'User is not logged in.'}, status=status.HTTP_400_BAD_REQUEST)
