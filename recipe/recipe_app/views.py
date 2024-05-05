import json
from decimal import Decimal

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


from .forms import IngredientForm, RecipeForm
from .models import Recipe, Ingredient, IngredientRecipe


def recipe_list(request):
    recipe_form = RecipeForm()
    ingredient_form = IngredientForm()
    ingredients = Ingredient.objects.all()  # Пример queryset для ингредиентов
    return render(request, 'recipe_list.html', {'recipe_form': recipe_form, 'ingredient_form': ingredient_form, 'ingredients': ingredients})


def create_recipe(request):
    ingredients = Ingredient.objects.all()  # Получаем все ингредиенты
    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST)
        ingredient_form = IngredientForm(request.POST)
        if recipe_form.is_valid() and ingredient_form.is_valid():
            recipe = recipe_form.save()  # Сохраняем рецепт
            for ingredient in ingredients:
                ingredient_id = str(ingredient.id)
                ingredient_quantity = request.POST.get('ingredient_quantity_' + ingredient_id)
                if ingredient_quantity:
                    recipe.ingredients.add(ingredient, through_defaults={'quantity': ingredient_quantity})
            return redirect('recipe_list')
    else:
        recipe_form = RecipeForm()
        ingredient_form = IngredientForm()
    return render(request, 'recipe_list.html', {'recipe_form': recipe_form, 'ingredient_form': ingredient_form, 'ingredients': ingredients})



def create_ingredient(request):
    if request.method == 'POST':
        # print('Here')
        form = IngredientForm(request.POST)
        # print(form.cleaned_data['name'])
        if form.is_valid():
            print('Here, valid')
            form.save()
            return redirect('recipe_list')
    return redirect('recipe_list')# Перенаправляем пользователя на список рецептов после создания ингредиента
    # else:
    #     form = IngredientForm()
    # return render(request, 'create_ingredient.html', {'form': form})



def recipies(request):
    recipes = Recipe.objects.all()
    res = []
    for recipe in recipes:
        ingredients_list = []
        for ingredient_recipe in recipe.ingredientrecipe_set.all():
            ingredients_list.append({
                'name': ingredient_recipe.ingredient.name,
                'amount': ingredient_recipe.ingredient_amount,
                'cost': ingredient_recipe.ingredient.cost
            })
        res.append({
            'id': recipe.id,
            'name': recipe.name,
            'image_url': recipe.image_url,
            'description': recipe.description,
            'ingredients': ingredients_list
        })
    return JsonResponse({'result': 'ok', 'data': res})


def get_ingredients(request):
    ingredients = Ingredient.objects.all()
    return JsonResponse({'result': 'ok', 'data': [{'id': i.id, 'name': i.name, 'cost': i.cost} for i in ingredients]})


@csrf_exempt
def ingredient(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # print(Decimal(int(data.get('price'))))
        ingr = Ingredient(name=data.get('name'), cost=Decimal(int(data.get('price'))))
        ingr.save()
        return JsonResponse({'result': 'ok'})


@csrf_exempt
def recipe(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        recipe = Recipe.objects.create(
            name=data.get('title'),
            image_url=data.get('image_url'),
            description=data.get('description')
        )
        recipe.save()
        for ingredient_data in data['ingredients']:
            ingredient_id = ingredient_data['ingredient']
            ingredient_amount = ingredient_data['quantity']

            ingredient = Ingredient.objects.get(pk=ingredient_id)

            ingredient_recipe = IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                ingredient_amount=ingredient_amount
            )
            ingredient_recipe.save()


        return JsonResponse({'result': 'ok'})