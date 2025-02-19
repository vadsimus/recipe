from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import IngredientSerializer, RecipeSerializer, UserRegistrationSerializer
from .models import Recipe, Ingredient


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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
        recipe = self.get_object()
        image = request.FILES.get('image')

        if not image:
            return Response({'error': 'Image not uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if image.content_type not in allowed_types:
            return Response(
                {'error': 'Unsupported image format. Allowed formats: JPEG, PNG, GIF.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        max_size = 5 * 1024 * 1024  # 5 MB
        if image.size > max_size:
            return Response(
                {'error': 'Image size exceeds the allowed limit (5 MB).'}, status=status.HTTP_400_BAD_REQUEST
            )

        recipe.image = image
        recipe.save()
        return Response({'message': 'Image successfully uploaded'}, status=status.HTTP_200_OK)


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ingredient.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_ingredient(request):
    serializer = IngredientSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({'result': 'ok'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# APIView for creating a recipe with ingredients
class CreateRecipeView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        recipe_serializer = RecipeSerializer(data=request.data, context={'request': request})
        if recipe_serializer.is_valid():
            recipe = recipe_serializer.save(user=request.user)
            return Response({'result': 'ok', 'recipe_id': recipe.id}, status=status.HTTP_201_CREATED)
        return Response(recipe_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ingredients(request):
    ingredients = Ingredient.objects.filter(user=request.user)
    serializer = IngredientSerializer(ingredients, many=True)
    return Response({'result': 'ok', 'data': serializer.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        if User.objects.filter(email=email).exists():
            return Response({'error': f"Email '{email}' is already in use."}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': f"Username '{username}' is already taken"}, status=status.HTTP_400_BAD_REQUEST)
        User.objects.create_user(username=username, email=email, password=password)
        return Response({'result': 'ok', 'message': 'User successfully registered.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
