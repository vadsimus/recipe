"""
URL configuration for recipe project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe_app import views

# Setting up the DRF router for viewsets
router = DefaultRouter()
router.register(r'recipes', views.RecipeViewSet, basename='recipe')
router.register(r'ingredients', views.IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),  # Includes the viewset routes
    path('recipes/create/', views.CreateRecipeView.as_view(), name='create_recipe'),  # Custom recipe creation view
    path('get_ingredients/', views.get_ingredients, name='get_ingredients'),  # Simple ingredient list view
    path('create_ingredient/', views.create_ingredient, name='create_ingredient'),  # Simple ingredient creation view
    path('api/register/', views.register_user, name='register_user'),
    path('api/login/', views.login_user, name='login_user'),
    path('api/logout/', views.logout_user, name='logout_user'),
]
