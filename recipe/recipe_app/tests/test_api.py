import uuid
import io
import pytest
import requests
from PIL import Image


@pytest.fixture
def base_url(live_server):
    return live_server.url


@pytest.fixture
def user_credentials():
    unique_str = str(uuid.uuid4())
    username = f"testuser_{unique_str}"
    email = f"{username}@example.com"
    password = "TestPass123"
    return {"username": username, "email": email, "password": password}


@pytest.fixture
def register_user(base_url, user_credentials):
    url = f"{base_url}/api/register/"
    response = requests.post(url, json=user_credentials)
    assert response.status_code == 201, f"Registration error: {response.text}"
    return user_credentials


@pytest.fixture
def auth_headers(base_url, register_user, user_credentials):
    token_url = f"{base_url}/api/token/"
    data = {"username": user_credentials["username"], "password": user_credentials["password"]}
    response = requests.post(token_url, json=data)
    assert response.status_code == 200, f"Token obtain error: {response.text}"
    token = response.json()["access"]
    return {"Authorization": f"Bearer {token}"}


def test_register_user(base_url, user_credentials):
    url = f"{base_url}/api/register/"
    response = requests.post(url, json=user_credentials)
    assert response.status_code == 201, f"Registration error: {response.text}"
    data = response.json()
    assert data["result"] == "ok"


def test_token_obtain(base_url, user_credentials):
    reg_url = f"{base_url}/api/register/"
    requests.post(reg_url, json=user_credentials)
    token_url = f"{base_url}/api/token/"
    resp = requests.post(
        token_url, json={"username": user_credentials["username"], "password": user_credentials["password"]}
    )
    assert resp.status_code == 200, f"Token obtain error: {resp.text}"
    j = resp.json()
    assert "access" in j and "refresh" in j


def test_create_ingredient(base_url, auth_headers):
    url = f"{base_url}/api/ingredients/"
    payload = {"name": "Sugar", "cost": 2.5}
    resp = requests.post(url, json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Ingredient creation error: {resp.text}"

    get_url = url
    get_resp = requests.get(get_url, headers=auth_headers)
    assert get_resp.status_code == 200, f"Ingredient retrieval error: {get_resp.text}"
    data = get_resp.json()["data"]
    assert any(ing["name"] == "Sugar" and float(ing["cost"]) == 2.5 for ing in data)


def test_create_recipe(base_url, auth_headers):
    ing_url = f"{base_url}/api/ingredients/"
    ing_payload = {"name": "Flour", "cost": 1.0}
    requests.post(ing_url, json=ing_payload, headers=auth_headers)

    ingredients = requests.get(ing_url, headers=auth_headers).json()["data"]
    flour = next(ing for ing in ingredients if ing["name"] == "Flour")
    assert flour

    recipe_url = f"{base_url}/api/recipes/"
    recipe_payload = {
        "name": "Bread",
        "description": "Fresh homemade bread",
        "ingredients": [{"ingredient_id": flour["id"], "ingredient_amount": 500}],
    }
    r = requests.post(recipe_url, json=recipe_payload, headers=auth_headers)
    assert r.status_code == 201, f"Recipe creation error: {r.text}"

    data = r.json()["data"]
    assert data["id"]
    assert data["name"] == "Bread"
    assert data["description"] == "Fresh homemade bread"
    assert len(data["ingredients"]) == 1
    item = data["ingredients"][0]
    assert item["id"] == flour["id"]
    assert item["name"] == "Flour"
    assert float(item["cost"]) == 1.0
    assert item["ingredient_amount"] == 500
    assert float(item["ingredient_price"]) == pytest.approx(500.0)
    assert float(data["total_price"]) == pytest.approx(500.0)


def test_list_recipes_with_ingredients(base_url, auth_headers):
    url = f"{base_url}/api/recipes/"
    resp = requests.get(url, headers=auth_headers)
    assert resp.status_code == 200, f"Error retrieving recipes: {resp.text}"
    data = resp.json()["data"]

    for recipe in data:
        assert "id" in recipe
        assert "name" in recipe
        assert "description" in recipe
        assert "ingredients" in recipe
        assert "total_price" in recipe
        for ing in recipe["ingredients"]:
            assert "id" in ing
            assert "name" in ing
            assert "cost" in ing
            assert "ingredient_amount" in ing
            assert "ingredient_price" in ing


def test_upload_recipe_image(base_url, auth_headers):
    recipe_url = f"{base_url}/api/recipes/"
    payload = {"name": "Pancakes", "description": "Yummy", "ingredients": []}
    cre = requests.post(recipe_url, json=payload, headers=auth_headers)
    recipe_id = cre.json()["data"]["id"]

    upload_url = f"{base_url}/api/recipes/{recipe_id}/upload-image/"

    img_buf = io.BytesIO()
    Image.new("RGB", (100, 100), "red").save(img_buf, format="PNG")
    img_buf.seek(0)
    files = {"image": ("test.png", img_buf, "image/png")}

    upl = requests.post(upload_url, files=files, headers=auth_headers)
    assert upl.status_code == 200, f"Image upload error: {upl.text}"

    j = upl.json()
    assert j["message"] == "Image successfully uploaded"
    d = j["data"]
    assert "ingredients" in d and isinstance(d["ingredients"], list)
    assert float(d["total_price"]) == pytest.approx(0.0)
    assert "image" in d and d["image"]


def test_edit_recipe(base_url, auth_headers):
    recipe_url = f"{base_url}/api/recipes/"
    base_payload = {"name": "Classic Pancakes", "description": "Tasty", "ingredients": []}
    cre = requests.post(recipe_url, json=base_payload, headers=auth_headers)
    rid = cre.json()["data"]["id"]

    ing_url = f"{base_url}/api/ingredients/"
    ing_payload = {"name": "Milk", "cost": 1.5}
    requests.post(ing_url, json=ing_payload, headers=auth_headers)
    milk = next(ing for ing in requests.get(ing_url, headers=auth_headers).json()["data"] if ing["name"] == "Milk")

    edit_url = f"{base_url}/api/recipes/{rid}/"
    upd = {
        "name": "Updated Pancakes",
        "description": "Fluffy with milk",
        "ingredients": [{"ingredient_id": milk["id"], "ingredient_amount": 200}],
    }
    patch = requests.patch(edit_url, json=upd, headers=auth_headers)
    assert patch.status_code == 200, f"Recipe update error: {patch.text}"

    d = patch.json()["data"]
    assert d["name"] == "Updated Pancakes"
    assert d["description"] == "Fluffy with milk"
    assert len(d["ingredients"]) == 1
    item = d["ingredients"][0]
    assert item["name"] == "Milk"
    assert item["ingredient_amount"] == 200
    assert float(item["ingredient_price"]) == pytest.approx(200 * float(milk["cost"]))
    assert pytest.approx(float(item["ingredient_price"])) == float(d["total_price"])
