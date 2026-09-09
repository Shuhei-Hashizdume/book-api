from fastapi.testclient import TestClient
from sqlalchemy import select

from main import app
from models import User
from security import decode_access_token, verify_password

client = TestClient(app)


def test_create_user(user_data, db_session):
    response = client.post("/users", json=user_data)

    assert response.status_code == 201
    response_data = response.json()

    assert set(response_data) == {"id", "username"}
    assert isinstance(response_data["id"], int)
    assert response_data["username"] == user_data["username"]

    statement = select(User).where(User.email == user_data["email"])
    user = db_session.scalar(statement)

    assert user is not None
    assert user.hashed_password != user_data["password"]
    assert verify_password(user_data["password"], user.hashed_password)


def test_login_user(user_data, registered_user):
    response = client.post(
        "/users/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"],
        },
    )

    assert response.status_code == 200
    response_data = response.json()

    assert set(response_data) == {"access_token", "token_type"}

    assert isinstance(response_data["access_token"], str)
    assert response_data["access_token"]
    assert response_data["token_type"] == "bearer"
    assert decode_access_token(response_data["access_token"]) == registered_user.id


def test_read_current_user(registered_user, access_token):
    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 200
    response_data = response.json()

    assert response_data == {
        "id": registered_user.id,
        "username": registered_user.username,
    }


def test_login_user_with_wrong_password(registered_user, user_data):
    response = client.post(
        "/users/login", json={"email": user_data["email"], "password": "wrong_password"}
    )

    assert response.status_code == 401
