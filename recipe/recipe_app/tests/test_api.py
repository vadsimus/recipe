import uuid
import io
import pytest
import requests
from PIL import Image

BASE_URL = "http://localhost:8000"  # Change if needed


@pytest.fixture
def user_credentials():
    # Generate unique username and email to avoid conflicts
    unique_str = str(uuid.uuid4())
    username = f"testuser_{unique_str}"
    email = f"{username}@example.com"
    password = "TestPass123"
    return {"username": username, "email": email, "password": password}


@pytest.fixture
def register_user(user_credentials):
    url = f"{BASE_URL}/api/register/"
    response = requests.post(url, json=user_credentials)
    assert response.status_code == 201, f"Registration error: {response.text}"
    return user_credentials


@pytest.fixture
def auth_headers(register_user, user_credentials):
    # Obtain JWT token via /api/token/ endpoint
    token_url = f"{BASE_URL}/api/token/"
    data = {
        "username": user_credentials["username"],
        "password": user_credentials["password"],
    }
    response = requests.post(token_url, json=data)
    assert response.status_code == 200, f"Token obtain error: {response.text}"
    token = response.json().get("access")
    headers = {"Authorization": f"Bearer {token}"}
    return headers


def test_register_user(user_credentials):
    url = f"{BASE_URL}/api/register/"
    response = requests.post(url, json=user_credentials)
    assert response.status_code == 201, f"Registration error: {response.text}"
    data = response.json()
    assert data.get("result") == "ok", "Registration response does not contain result = ok"


def test_token_obtain(user_credentials):
    # Register the user if not already registered
    reg_url = f"{BASE_URL}/api/register/"
    reg_response = requests.post(reg_url, json=user_credentials)
    assert reg_response.status_code == 201, f"Registration error: {reg_response.text}"

    token_url = f"{BASE_URL}/api/token/"
    data = {"username": user_credentials["username"], "password": user_credentials["password"]}
    response = requests.post(token_url, json=data)
    assert response.status_code == 200, f"Token obtain error: {response.text}"
    json_resp = response.json()
    assert "access" in json_resp, "Access token not received"
    assert "refresh" in json_resp, "Refresh token not received"


def test_create_ingredient(auth_headers):
    url = f"{BASE_URL}/api/ingredients/"
    payload = {"name": "Sugar", "cost": 2.5}
    response = requests.post(url, json=payload, headers=auth_headers)
    assert response.status_code == 201, f"Ingredient creation error: {response.text}"
    # Verify ingredient list retrieval
    get_url = f"{BASE_URL}/api/ingredients/"
    get_response = requests.get(get_url, headers=auth_headers)
    assert get_response.status_code == 200, f"Ingredient retrieval error: {get_response.text}"
    data = get_response.json().get("data", [])
    assert any(ing["name"] == "Sugar" for ing in data), "Ingredient 'Sugar' not found in list"


def test_create_recipe(auth_headers):
    # First, create an ingredient to be used in the recipe
    ingredient_url = f"{BASE_URL}/api/ingredients/"
    ingredient_payload = {"name": "Flour", "cost": 1.0}
    ing_response = requests.post(ingredient_url, json=ingredient_payload, headers=auth_headers)
    assert ing_response.status_code == 201, f"Ingredient creation error: {ing_response.text}"

    # Retrieve ingredient list to get the created ingredient's id
    get_ing_url = f"{BASE_URL}/api/ingredients/"
    get_ing_response = requests.get(get_ing_url, headers=auth_headers)
    ingredients = get_ing_response.json().get("data", [])
    flour = next((ing for ing in ingredients if ing["name"] == "Flour"), None)
    assert flour is not None, "Ingredient 'Flour' not found"

    # Create a recipe using the created ingredient
    recipe_url = f"{BASE_URL}/api/recipes/"
    recipe_payload = {
        "name": "Bread",
        "description": "Fresh homemade bread",
        "ingredients": [{"ingredient_id": flour["id"], "ingredient_amount": 500}],
    }
    recipe_response = requests.post(recipe_url, json=recipe_payload, headers=auth_headers)
    assert recipe_response.status_code == 201, f"Recipe creation error: {recipe_response.text}"
    recipe_data = recipe_response.json()
    assert "id" in recipe_data['data'], "Recipe ID not returned"


def test_list_recipes_with_ingredients(auth_headers):
    # Endpoint for retrieving recipes with detailed ingredient info
    url = f"{BASE_URL}/api/recipes/"
    response = requests.get(url, headers=auth_headers)
    assert response.status_code == 200, f"Error retrieving recipes: {response.text}"
    data = response.json().get("data", [])
    if data:
        for recipe in data:
            assert "id" in recipe
            assert "name" in recipe
            assert "description" in recipe
            assert "ingredients" in recipe
            for ingredient in recipe["ingredients"]:
                assert "name" in ingredient
                assert "amount" in ingredient
                assert "cost" in ingredient


def test_upload_recipe_image(auth_headers):
    # Create a recipe without an image
    recipe_url = f"{BASE_URL}/api/recipes/"
    recipe_payload = {"name": "Pancakes", "image": None, "description": "Delicious pancakes", "ingredients": []}
    recipe_response = requests.post(recipe_url, json=recipe_payload, headers=auth_headers)
    assert recipe_response.status_code == 201, f"Recipe creation error: {recipe_response.text}"
    recipe_id = recipe_response.json().get('data', {}).get("id")
    assert recipe_id, "Recipe ID not returned"

    # Upload an image for the created recipe
    upload_url = f"{BASE_URL}/api/recipes/{recipe_id}/upload-image/"

    # Create an in-memory image (PNG)
    img_bytes = io.BytesIO()
    image = Image.new('RGB', (100, 100), color='red')
    image.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    files = {'image': ('test.png', img_bytes, 'image/png')}
    upload_response = requests.post(upload_url, files=files, headers=auth_headers)
    assert upload_response.status_code == 200, f"Image upload error: {upload_response.text}"
    resp_json = upload_response.json()
    assert resp_json.get("message") == "Image successfully uploaded", "Incorrect upload message"


def test_edit_recipe(auth_headers):
    # First, create a recipe
    recipe_url = f"{BASE_URL}/api/recipes/"
    recipe_payload = {"name": "Classic Pancakes", "description": "Simple and delicious pancakes", "ingredients": []}
    recipe_response = requests.post(recipe_url, json=recipe_payload, headers=auth_headers)
    assert recipe_response.status_code == 201, f"Recipe creation error: {recipe_response.text}"

    recipe_data = recipe_response.json()
    recipe_id = recipe_data.get('data', {}).get("id")
    assert recipe_id, "Recipe ID not returned"

    # Create an ingredient for editing the recipe
    ingredient_url = f"{BASE_URL}/api/ingredients/"
    ingredient_payload = {"name": "Milk", "cost": 1.5}
    ing_response = requests.post(ingredient_url, json=ingredient_payload, headers=auth_headers)
    assert ing_response.status_code == 201, f"Ingredient creation error: {ing_response.text}"

    # Get the created ingredient's ID
    get_ing_url = f"{BASE_URL}/api/ingredients/"
    get_ing_response = requests.get(get_ing_url, headers=auth_headers)
    ingredients = get_ing_response.json().get("data", [])
    milk = next((ing for ing in ingredients if ing["name"] == "Milk"), None)
    assert milk is not None, "Ingredient 'Milk' not found"

    # Prepare data for updating the recipe
    edit_url = f"{BASE_URL}/api/recipes/{recipe_id}/"
    updated_payload = {
        "name": "Updated Pancakes",
        "description": "Fluffy and tasty pancakes with milk",
        "ingredients": [{"ingredient_id": milk["id"], "ingredient_amount": 200}],
    }

    # Send PATCH request to update the recipe
    edit_response = requests.patch(edit_url, json=updated_payload, headers=auth_headers)
    assert edit_response.status_code == 200, f"Recipe update error: {edit_response.text}"
    updated_data = edit_response.json()
    assert updated_data.get('data')["name"] == "Updated Pancakes", "Recipe name was not updated"
    assert (
        updated_data.get('data')["description"] == "Fluffy and tasty pancakes with milk"
    ), "Recipe description was not updated"
    assert len(updated_data.get('data')["ingredients"]) == 1, "Ingredients were not added"
    assert updated_data.get('data')["ingredients"][0]["ingredient"]["name"] == "Milk", "Incorrect ingredient added"
    assert updated_data.get('data')["ingredients"][0]["ingredient_amount"] == 200, "Incorrect ingredient quantity"
