import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from enums import ReadingPriority, ReadingStatus
from main import app
from models import Book, UserBook

client = TestClient(app)


def test_read_books():
    response = client.get("/books")

    assert response.status_code == 200
    assert response.json() == []


def test_read_books_returns_books(book_in_db):
    response = client.get("/books")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": book_in_db.id,
            "title": "テスト用の本",
            "author": "テスト著者",
        }
    ]


def test_read_book_returns_detail_without_recommendation_score(book_in_db):
    response = client.get(f"/books/{book_in_db.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": book_in_db.id,
        "title": "テスト用の本",
        "author": "テスト著者",
        "genre": "other",
        "average_recommendation_score": None,
    }


def test_read_book_returns_average_recommendation_score(
    user_book_data,
    registered_user,
    other_user,
    third_user,
    db_session,
):
    first_user_book = UserBook(
        user_id=registered_user.id,
        book_id=user_book_data["book_id"],
        priority=ReadingPriority.HIGH,
        status=ReadingStatus.COMPLETED,
        recommendation_score=5,
    )
    second_user_book = UserBook(
        user_id=other_user.id,
        book_id=user_book_data["book_id"],
        priority=ReadingPriority.HIGH,
        status=ReadingStatus.COMPLETED,
        recommendation_score=4,
    )
    third_user_book = UserBook(
        user_id=third_user.id,
        book_id=user_book_data["book_id"],
        priority=ReadingPriority.HIGH,
        status=ReadingStatus.COMPLETED,
        recommendation_score=4,
    )

    db_session.add(first_user_book)
    db_session.add(second_user_book)
    db_session.add(third_user_book)
    db_session.commit()

    response = client.get(f'/books/{user_book_data["book_id"]}')

    assert response.status_code == 200
    assert response.json()["average_recommendation_score"] == 4.3


def test_read_book_not_found():
    response = client.get("/books/999999")

    assert response.status_code == 404


@pytest.mark.parametrize("book_id", ["abc", "0", "-1"])
def test_read_book_rejects_invalid_book_id(book_id):
    response = client.get(f"/books/{book_id}")

    assert response.status_code == 422


def test_create_book(book_data, admin_access_token, db_session):
    response = client.post(
        "/books",
        headers={"Authorization": f"Bearer {admin_access_token}"},
        json=book_data,
    )

    assert response.status_code == 201
    response_data = response.json()

    assert response_data["title"] == book_data["title"]
    assert response_data["author"] == book_data["author"]
    assert isinstance(response_data["id"], int)

    statement = select(Book).where(Book.isbn == book_data["isbn"])
    book = db_session.scalar(statement)

    assert book is not None
    assert response_data["id"] == book.id


def test_create_book_forbidden_for_non_admin(book_data, access_token, db_session):
    response = client.post(
        "/books", json=book_data, headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 403

    statement = select(Book).where(Book.isbn == book_data["isbn"])
    book = db_session.scalar(statement)

    assert book is None


def test_create_book_unauthorized_without_token(book_data, db_session):
    response = client.post("/books", json=book_data)

    assert response.status_code == 401

    statement = select(Book).where(Book.isbn == book_data["isbn"])
    book = db_session.scalar(statement)

    assert book is None


def test_create_book_conflict_with_duplicate_isbn(book_data, admin_access_token):
    response = client.post(
        "/books",
        json=book_data,
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )

    assert response.status_code == 201

    second_response = client.post(
        "/books",
        json=book_data,
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )

    assert second_response.status_code == 409


def test_update_book(book_in_db, admin_access_token, db_session):
    response = client.patch(
        f"/books/{book_in_db.id}",
        json={"title": "テストB"},
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )

    assert response.status_code == 200
    response_data = response.json()

    assert response_data["title"] == "テストB"
    assert response_data["author"] == "テスト著者"

    update_book = db_session.get(Book, book_in_db.id)
    assert update_book is not None
    assert update_book.title == "テストB"


def test_delete_book(book_data, admin_access_token, db_session):
    post_response = client.post(
        "/books",
        json=book_data,
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )
    assert post_response.status_code == 201

    book_id = post_response.json()["id"]

    delete_response = client.delete(
        f"/books/{book_id}", headers={"Authorization": f"Bearer {admin_access_token}"}
    )
    assert delete_response.status_code == 204

    book = db_session.get(Book, book_id)

    assert book is None
