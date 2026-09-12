import pytest
from fastapi.testclient import TestClient

from main import app
from models import Book, UserBook

client = TestClient(app)


def test_create_user_book(user_book_data, access_token, db_session, registered_user):
    response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 201
    response_data = response.json()

    assert response_data["book_id"] == user_book_data["book_id"]
    assert response_data["priority"] == user_book_data["priority"]
    assert isinstance(response_data["id"], int)
    assert set(response_data) == {
        "id",
        "book_id",
        "priority",
        "status",
        "recommendation_score",
    }
    assert response_data["status"] == "want_to_read"
    assert response_data["recommendation_score"] is None

    user_book = db_session.get(UserBook, response_data["id"])

    assert user_book is not None
    assert user_book.user_id == registered_user.id
    assert user_book.book_id == user_book_data["book_id"]
    assert user_book.priority.value == user_book_data["priority"]
    assert user_book.status.value == "want_to_read"
    assert user_book.recommendation_score is None


def test_create_user_book_conflict_with_duplicate_book(user_book_data, access_token):
    response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 201

    second_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert second_response.status_code == 409


def test_create_user_book_not_found(access_token):
    response = client.post(
        "/users/me/books",
        json={"book_id": 0, "priority": "high"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404


def test_create_user_book_unauthorized_without_token(user_book_data):
    response = client.post("/users/me/books", json=user_book_data)

    assert response.status_code == 401


def test_create_user_book_rejects_invalid_priority(user_book_data, access_token):
    response = client.post(
        "/users/me/books",
        json={"book_id": user_book_data["book_id"], "priority": "urgent"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422


def test_read_user_books(user_book_data, access_token, book_in_db):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert post_response.status_code == 201
    post_response_data = post_response.json()

    get_response = client.get(
        "/users/me/books", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert get_response.status_code == 200

    get_response_data = get_response.json()

    assert get_response_data[0]["id"] == post_response_data["id"]
    assert get_response_data[0]["priority"] == user_book_data["priority"]
    assert get_response_data[0]["book"]["title"] == book_in_db.title
    assert get_response_data[0]["book"]["id"] == book_in_db.id
    assert get_response_data[0]["book"]["author"] == book_in_db.author
    assert len(get_response_data) == 1


def test_update_user_book_priority(access_token, db_session, user_book_data):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert post_response.status_code == 201

    target_book_id = post_response.json()["book_id"]

    patch_response = client.patch(
        f"/users/me/books/{target_book_id}",
        json={"priority": "medium"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert patch_response.status_code == 200

    patch_response_data = patch_response.json()
    assert patch_response_data["priority"] == "medium"
    assert patch_response_data["book_id"] == user_book_data["book_id"]
    assert post_response.json()["id"] == patch_response.json()["id"]

    user_book = db_session.get(UserBook, patch_response_data["id"])

    assert user_book is not None
    assert user_book.priority.value == "medium"


def test_update_user_book_priority_not_found(book_in_db, access_token, db_session):
    response = client.patch(
        f"/users/me/books/{book_in_db.id}",
        json={"priority": "medium"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404


def test_delete_user_book(db_session, access_token, user_book_data):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert post_response.status_code == 201
    target_book_id = post_response.json()["book_id"]
    user_book_id = post_response.json()["id"]

    delete_response = client.delete(
        f"/users/me/books/{target_book_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert delete_response.status_code == 204

    user_book = db_session.get(UserBook, user_book_id)
    assert user_book is None

    book = db_session.get(Book, target_book_id)
    assert book is not None


def test_update_user_book_status_to_reading(user_book_data, access_token, db_session):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    post_response_data = post_response.json()

    assert post_response.status_code == 201
    assert post_response_data["status"] == "want_to_read"

    target_book_id = post_response_data["book_id"]

    patch_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "reading"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    patch_response_data = patch_response.json()

    assert patch_response.status_code == 200
    assert patch_response_data["status"] == "reading"
    assert post_response_data["id"] == patch_response_data["id"]

    user_book = db_session.get(UserBook, patch_response_data["id"])
    assert user_book is not None
    assert user_book.status.value == "reading"


def test_update_user_book_status_to_completed_without_rating(
    user_book_data, access_token, db_session
):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    post_response_data = post_response.json()

    assert post_response.status_code == 201
    assert post_response_data["status"] == "want_to_read"

    target_book_id = post_response_data["book_id"]

    patch_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert patch_response.status_code == 409

    user_book = db_session.get(UserBook, post_response_data["id"])
    assert user_book is not None
    assert user_book.status.value == "want_to_read"


def test_update_user_book_status_invalid(user_book_data, access_token, db_session):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    post_response_data = post_response.json()

    assert post_response.status_code == 201
    assert post_response_data["status"] == "want_to_read"

    target_book_id = post_response_data["book_id"]

    patch_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "paused"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert patch_response.status_code == 422

    user_book = db_session.get(UserBook, post_response_data["id"])
    assert user_book is not None
    assert user_book.status.value == "want_to_read"


def test_update_user_book_status_not_found(book_in_db, access_token):
    response = client.patch(
        f"/users/me/books/{book_in_db.id}/status",
        json={"status": "reading"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404


def test_update_user_book_status_unauthorized(book_in_db):
    response = client.patch(
        f"/users/me/books/{book_in_db.id}/status", json={"status": "reading"}
    )
    assert response.status_code == 401


def test_user_book_status_to_completed_with_recommendation_score(
    access_token, user_book_data, db_session
):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert post_response.status_code == 201

    post_response_data = post_response.json()
    assert post_response_data["status"] == "want_to_read"
    assert post_response_data["recommendation_score"] is None
    target_book_id = post_response_data["book_id"]

    patch_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert patch_response.status_code == 200
    patch_response_data = patch_response.json()
    assert patch_response_data["id"] == post_response_data["id"]
    assert patch_response_data["status"] == "completed"
    assert patch_response_data["recommendation_score"] == 5

    user_book = db_session.get(UserBook, patch_response_data["id"])
    assert user_book is not None
    assert user_book.status.value == "completed"
    assert user_book.recommendation_score == 5


def test_update_user_book_recommendation_score(
    user_book_data, access_token, db_session
):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert post_response.status_code == 201

    post_response_data = post_response.json()
    target_book_id = post_response_data["book_id"]

    status_patch_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert status_patch_response.status_code == 200
    status_patch_response_data = status_patch_response.json()
    assert status_patch_response_data["status"] == "completed"
    assert post_response_data["id"] == status_patch_response_data["id"]

    patch_response = client.patch(
        f"/users/me/books/{target_book_id}/recommendation-score",
        json={"recommendation_score": 4},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert patch_response.status_code == 200
    patch_response_data = patch_response.json()
    assert patch_response_data["recommendation_score"] == 4
    assert status_patch_response_data["id"] == patch_response_data["id"]
    assert patch_response_data["status"] == "completed"

    user_book = db_session.get(UserBook, patch_response_data["id"])
    assert user_book is not None
    assert user_book.recommendation_score == 4
    assert user_book.status.value == "completed"


def test_update_user_book_recommendation_score_before_completed(
    user_book_data, access_token, db_session
):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert post_response.status_code == 201
    post_response_data = post_response.json()
    target_book_id = post_response_data["book_id"]

    patch_response = client.patch(
        f"/users/me/books/{target_book_id}/recommendation-score",
        json={"recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert patch_response.status_code == 409

    user_book = db_session.get(UserBook, post_response_data["id"])
    assert user_book is not None
    assert user_book.status.value == "want_to_read"
    assert user_book.recommendation_score is None


@pytest.mark.parametrize("recommendation_score", [0, 6])
def test_update_user_book_recommendation_score_with_outrange(
    user_book_data, access_token, db_session, recommendation_score
):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert post_response.status_code == 201

    post_response_data = post_response.json()
    target_book_id = post_response_data["book_id"]

    status_patch_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert status_patch_response.status_code == 200
    status_patch_response_data = status_patch_response.json()
    assert status_patch_response_data["status"] == "completed"
    assert post_response_data["id"] == status_patch_response_data["id"]

    patch_response = client.patch(
        f"/users/me/books/{target_book_id}/recommendation-score",
        json={"recommendation_score": recommendation_score},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert patch_response.status_code == 422

    user_book = db_session.get(UserBook, status_patch_response_data["id"])
    assert user_book is not None
    assert user_book.recommendation_score == 5


def test_update_user_book_recommendation_score_not_found(book_in_db, access_token):
    patch_response = client.patch(
        f"/users/me/books/{book_in_db.id}/recommendation-score",
        json={"recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert patch_response.status_code == 404


def test_update_user_book_recommendation_score_unauthorized(book_in_db):
    patch_response = client.patch(
        f"/users/me/books/{book_in_db.id}/recommendation-score",
        json={"recommendation_score": 5},
    )

    assert patch_response.status_code == 401
