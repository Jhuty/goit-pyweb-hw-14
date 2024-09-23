import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def auth(client):
    # Регистрируем и авторизуем пользователя
    client.post("/register", json={"username": "testuser", "password": "testpassword"})
    response = client.post("/login", data={"username": "testuser", "password": "testpassword"})
    return response.json()["access_token"]

def test_create_contact(client, auth):
    headers = {"Authorization": f"Bearer {auth}"}
    response = client.post(
        "/contacts/",
        headers=headers,
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "1234567890",
            "birthday": "1990-01-01",
            "additional_info": "Friend"
        }
    )
    assert response.status_code == 201
    assert "id" in response.json()

def test_update_contact(client, auth):
    headers = {"Authorization": f"Bearer {auth}"}
    contact_id = 1  # предполагаем, что контакт с ID 1 был создан
    response = client.put(
        f"/contacts/{contact_id}",
        headers=headers,
        json={"first_name": "Jane", "last_name": "Doe"}
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Jane"

def test_get_all_contacts(client, auth):
    headers = {"Authorization": f"Bearer {auth}"}
    response = client.get("/contacts/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
