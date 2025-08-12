# Register your models here.

from django.contrib import admin
from .models import Recipe, Ingredient, IngredientRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user')
    search_fields = ('name', 'user__username')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cost', 'unit', 'user')
    list_filter = ('unit',)
    search_fields = ('name', 'user__username')


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'ingredient_amount')
    search_fields = ('recipe__name', 'ingredient__name')
