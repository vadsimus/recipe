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
from django.urls import path

from recipe_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.recipe_list, name='recipe_list'),
    path('create-recipe/', views.create_recipe, name='create_recipe'),
    path('recipies/', views.recipies, name='create_recipe'),
    path('create-ingredient/', views.create_ingredient, name='create_ingredient'),
    path('get_ingredients/', views.get_ingredients, name='get_ingredients'),
    path('ingredient/', views.ingredient, name='ingredient'),
    path('recipe/', views.recipe, name='recipe'),
]

