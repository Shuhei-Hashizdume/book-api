from fastapi.testclient import TestClient
from sqlalchemy import select

from main import app
from models import Book

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


def test_read_books_return_book(book_in_db):
    response = client.get(f"/books/{book_in_db.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": book_in_db.id,
        "title": "テスト用の本",
        "author": "テスト著者",
    }


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
