import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from main import app
from models import Book, BookRating, UserBook

client = TestClient(app)


def test_list_books():
    response = client.get("/books")

    assert response.status_code == 200
    assert response.json() == []


def test_list_books_returns_books(book_in_db):
    response = client.get("/books")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": book_in_db.id,
            "title": "テスト用の本",
            "author": "テスト著者",
            "cover_image_url": None,
        }
    ]


def test_get_book_detail_returns_detail_without_recommendation_score(book_in_db):
    response = client.get(f"/books/{book_in_db.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": book_in_db.id,
        "title": "テスト用の本",
        "author": "テスト著者",
        "cover_image_url": None,
        "genre": "other",
        "average_recommendation_score": None,
    }


def test_get_book_detail_returns_cover_image_url(db_session):
    book = Book(
        title="表紙画像のある本",
        author="テスト著者",
        isbn="9780000000016",
        cover_image_url="https://example.com/book-cover.jpg",
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)

    try:
        response = client.get(f"/books/{book.id}")

        assert response.status_code == 200
        assert response.json() == {
            "id": book.id,
            "title": "表紙画像のある本",
            "author": "テスト著者",
            "cover_image_url": "https://example.com/book-cover.jpg",
            "genre": "other",
            "average_recommendation_score": None,
        }
    finally:
        db_session.delete(book)
        db_session.commit()


def test_get_book_detail_returns_average_recommendation_score(
    user_book_data,
    registered_user,
    other_user,
    third_user,
    db_session,
):
    first_book_rating = BookRating(
        user_id=registered_user.id,
        book_id=user_book_data["book_id"],
        recommendation_score=5,
    )
    second_book_rating = BookRating(
        user_id=other_user.id,
        book_id=user_book_data["book_id"],
        recommendation_score=4,
    )
    third_book_rating = BookRating(
        user_id=third_user.id,
        book_id=user_book_data["book_id"],
        recommendation_score=4,
    )

    db_session.add(first_book_rating)
    db_session.add(second_book_rating)
    db_session.add(third_book_rating)
    db_session.commit()

    try:
        response = client.get(f'/books/{user_book_data["book_id"]}')

        assert response.status_code == 200
        assert response.json()["average_recommendation_score"] == 4.3
    finally:
        db_session.rollback()
        db_session.delete(first_book_rating)
        db_session.delete(second_book_rating)
        db_session.delete(third_book_rating)
        db_session.commit()


def test_get_book_detail_not_found():
    response = client.get("/books/999999")

    assert response.status_code == 404


@pytest.mark.parametrize("book_id", ["abc", "0", "-1"])
def test_get_book_detail_rejects_invalid_book_id(book_id):
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


@pytest.mark.parametrize("book_id", ["abc", 0, -1])
def test_update_book_rejects_invalid_book_id(book_id, admin_access_token):
    response = client.patch(
        f"/books/{book_id}",
        json={"title": "テストB"},
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "book_id"]


@pytest.mark.parametrize("book_id", ["abc", 0, -1])
def test_delete_book_rejects_invalid_book_id(book_id, admin_access_token):
    response = client.delete(
        f"/books/{book_id}",
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "book_id"]


def test_delete_book_returns_conflict_when_book_is_in_user_list(
    user_book_data, access_token, admin_access_token, db_session
):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert post_response.status_code == 201
    book_id = post_response.json()["book_id"]
    user_book_id = post_response.json()["id"]

    delete_response = client.delete(
        f"/books/{book_id}",
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )
    assert delete_response.status_code == 409
    assert delete_response.json() == {
        "detail": "この本はユーザーの記録で使用されているため、削除できません。"
    }

    book_statement = select(Book).where(Book.id == book_id)
    assert db_session.scalar(book_statement) is not None
    user_book_statement = select(UserBook).where(UserBook.id == user_book_id)
    assert db_session.scalar(user_book_statement) is not None


def test_delete_book_returns_conflict_when_rating_exists(
    book_in_db, registered_user, admin_access_token, db_session
):
    book_id = book_in_db.id
    user_id = registered_user.id
    book_rating = BookRating(
        user_id=user_id,
        book_id=book_id,
        recommendation_score=5,
    )
    db_session.add(book_rating)
    db_session.commit()
    db_session.refresh(book_rating)
    book_rating_id = book_rating.id

    try:
        user_book_statement = select(UserBook).where(
            UserBook.user_id == user_id, UserBook.book_id == book_id
        )
        assert db_session.scalar(user_book_statement) is None

        delete_response = client.delete(
            f"/books/{book_id}",
            headers={"Authorization": f"Bearer {admin_access_token}"},
        )
        assert delete_response.status_code == 409
        assert delete_response.json() == {
            "detail": "この本はユーザーの記録で使用されているため、削除できません。"
        }

        book_statement = select(Book).where(Book.id == book_id)
        assert db_session.scalar(book_statement) is not None
        book_rating_statement = select(BookRating).where(BookRating.id == book_rating_id)
        saved_rating = db_session.scalar(book_rating_statement)
        assert saved_rating is not None
        assert saved_rating.recommendation_score == 5
    finally:
        db_session.delete(book_rating)
        db_session.commit()


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
