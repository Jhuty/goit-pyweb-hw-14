import unittest
from fastapi.testclient import TestClient
from main import app
from db import get_db, SessionLocal
from models import Base
import pytest


@pytest.fixture(scope="module")
def test_db():
    # Создаем временную базу данных
    engine = SessionLocal()
    Base.metadata.create_all(bind=engine)

    yield engine  # Возвращаем сессию для использования в тестах

    # Удаляем базу данных после тестов
    Base.metadata.drop_all(bind=engine)

class TestUserAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_register_user(self):
        response = self.client.post("/register", json={"username": "testuser", "password": "testpassword"})
        self.assertEqual(response.status_code, 201)
        self.assertIn("User registered successfully", response.json().get("message"))

    def test_login_user(self):
        response = self.client.post("/login", data={"username": "testuser", "password": "testpassword"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())

class TestContacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # Сначала зарегистрируем и авторизуем пользователя
        cls.client.post("/register", json={"username": "testuser", "password": "testpassword"})
        login_response = cls.client.post("/login", data={"username": "testuser", "password": "testpassword"})
        cls.access_token = login_response.json().get("access_token")

    def test_create_contact(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = self.client.post(
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
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json())

    def test_read_contact(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        contact_id = 1  # предполагаем, что контакт с ID 1 был создан
        response = self.client.get(f"/contacts/{contact_id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], contact_id)

    def test_delete_contact(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        contact_id = 1  # предполагаем, что контакт с ID 1 был создан
        response = self.client.delete(f"/contacts/{contact_id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())

if __name__ == "__main__":
    unittest.main()
