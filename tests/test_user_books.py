import httpx2
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from enums import BookGenre
from main import app
from models import Book, UserBook
from routers import user_books
from schemas.books import BookSearchResult

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


def test_read_user_books(user_book_data, access_token, book_in_db, db_session):
    book = db_session.get(Book, book_in_db.id)
    assert book is not None
    book.cover_image_url = "https://example.com/my-bookshelf-cover.jpg"
    db_session.commit()

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
    assert (
        get_response_data[0]["book"]["cover_image_url"]
        == "https://example.com/my-bookshelf-cover.jpg"
    )
    assert len(get_response_data) == 1


def test_read_user_book_detail_returns_registered_state(
    user_book_data,
    access_token,
    book_in_db,
):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert post_response.status_code == 201

    response = client.get(
        f"/users/me/books/{book_in_db.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "book": {
            "id": book_in_db.id,
            "title": "テスト用の本",
            "author": "テスト著者",
            "cover_image_url": None,
            "genre": "other",
            "average_recommendation_score": None,
        },
        "is_registered": True,
        "priority": "high",
        "status": "want_to_read",
        "recommendation_score": None,
    }


def test_read_user_book_detail_returns_unregistered_state(
    access_token,
    book_in_db,
):
    response = client.get(
        f"/users/me/books/{book_in_db.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "book": {
            "id": book_in_db.id,
            "title": "テスト用の本",
            "author": "テスト著者",
            "cover_image_url": None,
            "genre": "other",
            "average_recommendation_score": None,
        },
        "is_registered": False,
        "priority": None,
        "status": None,
        "recommendation_score": None,
    }


def test_read_user_book_detail_unauthorized_without_token(book_in_db):
    response = client.get(f"/users/me/books/{book_in_db.id}")

    assert response.status_code == 401


@pytest.mark.parametrize("book_id", ["abc", "0", "-1"])
def test_read_user_book_detail_rejects_invalid_book_id(
    book_id,
    access_token,
):
    response = client.get(
        f"/users/me/books/{book_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422


def test_read_user_book_detail_not_found(access_token):
    response = client.get(
        "/users/me/books/999999",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404


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


@pytest.mark.parametrize("isbn", ["9780000000011", None])
def test_create_user_book_from_search_creates_book_and_user_book(
    monkeypatch,
    access_token,
    db_session,
    registered_user,
    book_in_db,
    isbn,
):
    def fake_get_google_book(external_id: str) -> BookSearchResult:
        assert external_id == "abc123"

        return BookSearchResult(
            external_id="abc123",
            title="検索結果の本",
            author="著者A / 著者B",
            isbn=isbn,
            genre=BookGenre.MANGA,
            cover_image_url="https://example.com/new-book-small.jpg",
        )

    monkeypatch.setattr(
        user_books,
        "get_google_book",
        fake_get_google_book,
    )

    response = client.post(
        "/users/me/books/from-search",
        json={
            "external_id": "abc123",
            "priority": "high",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 201
    response_data = response.json()
    assert isinstance(response_data["id"], int)
    assert isinstance(response_data["book_id"], int)
    assert response_data["priority"] == "high"
    assert response_data["status"] == "want_to_read"
    assert response_data["recommendation_score"] is None
    assert set(response_data) == {
        "id",
        "book_id",
        "priority",
        "status",
        "recommendation_score",
    }

    saved_book = db_session.get(Book, response_data["book_id"])

    assert saved_book is not None
    assert saved_book.id != book_in_db.id
    assert saved_book.external_id == "abc123"
    assert saved_book.title == "検索結果の本"
    assert saved_book.author == "著者A / 著者B"
    assert saved_book.isbn == isbn
    assert saved_book.genre == BookGenre.MANGA
    assert saved_book.cover_image_url == "https://example.com/new-book-small.jpg"

    saved_user_book = db_session.get(UserBook, response_data["id"])

    assert saved_user_book is not None
    assert saved_user_book.user_id == registered_user.id
    assert saved_user_book.book_id == saved_book.id
    assert saved_user_book.priority.value == "high"
    assert saved_user_book.status.value == "want_to_read"
    assert saved_user_book.recommendation_score is None

    db_session.delete(saved_user_book)
    db_session.flush()
    db_session.delete(saved_book)
    db_session.commit()


@pytest.mark.parametrize(
    "existing_external_id", [None, "existing-book-id", "saved-google-id"]
)
def test_create_user_book_from_search_reuses_existing_book(
    monkeypatch,
    access_token,
    db_session,
    existing_external_id,
):
    existing_book = Book(
        external_id=existing_external_id,
        title="DBに保存済みのタイトル",
        author="DBに保存済みの著者",
        isbn="9780000000012",
    )
    db_session.add(existing_book)
    db_session.commit()
    db_session.refresh(existing_book)

    assert existing_book.genre == BookGenre.OTHER

    existing_book_id = existing_book.id
    existing_title = existing_book.title
    existing_author = existing_book.author

    def fake_get_google_book(external_id: str) -> BookSearchResult:
        assert external_id == "existing-book-id"

        return BookSearchResult(
            external_id="existing-book-id",
            title="Google Books側のタイトル",
            author="Google Books側の著者",
            isbn="9780000000012",
            genre=BookGenre.BUSINESS,
            cover_image_url="https://example.com/existing-book-small.jpg",
        )

    monkeypatch.setattr(
        user_books,
        "get_google_book",
        fake_get_google_book,
    )

    response = client.post(
        "/users/me/books/from-search",
        json={
            "external_id": "existing-book-id",
            "priority": "medium",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["book_id"] == existing_book_id
    assert response_data["priority"] == "medium"

    saved_user_book = db_session.get(UserBook, response_data["id"])

    assert saved_user_book is not None
    assert saved_user_book.book_id == existing_book_id

    db_session.refresh(existing_book)
    assert existing_book.external_id == (
        existing_external_id if existing_external_id is not None else "existing-book-id"
    )
    assert existing_book.title == existing_title
    assert existing_book.author == existing_author
    assert existing_book.isbn == "9780000000012"
    assert existing_book.genre == BookGenre.BUSINESS
    assert (
        existing_book.cover_image_url
        == "https://example.com/existing-book-small.jpg"
    )

    db_session.delete(saved_user_book)
    db_session.flush()
    db_session.delete(existing_book)
    db_session.commit()


def test_create_user_book_from_search_preserves_existing_cover_image_url(
    monkeypatch,
    access_token,
    db_session,
):
    existing_book = Book(
        title="画像設定済みの本",
        author="著者A",
        isbn="9780000000015",
        cover_image_url="https://example.com/saved-cover.jpg",
    )
    db_session.add(existing_book)
    db_session.commit()
    db_session.refresh(existing_book)

    existing_book_id = existing_book.id

    def fake_get_google_book(external_id: str) -> BookSearchResult:
        assert external_id == "book-with-existing-cover"

        return BookSearchResult(
            external_id="book-with-existing-cover",
            title="Google Books側のタイトル",
            author="Google Books側の著者",
            isbn="9780000000015",
            genre=BookGenre.OTHER,
            cover_image_url="https://example.com/google-cover.jpg",
        )

    monkeypatch.setattr(
        user_books,
        "get_google_book",
        fake_get_google_book,
    )

    response = client.post(
        "/users/me/books/from-search",
        json={
            "external_id": "book-with-existing-cover",
            "priority": "medium",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["book_id"] == existing_book_id

    saved_user_book = db_session.get(UserBook, response_data["id"])
    assert saved_user_book is not None

    db_session.refresh(existing_book)
    assert existing_book.cover_image_url == "https://example.com/saved-cover.jpg"

    db_session.delete(saved_user_book)
    db_session.flush()
    db_session.delete(existing_book)
    db_session.commit()


def test_create_user_book_from_search_preserves_existing_genre(
    monkeypatch,
    access_token,
    db_session,
):
    existing_book = Book(
        title="ジャンル設定済みの本",
        author="著者A",
        isbn="9780000000014",
        genre=BookGenre.HUMANITIES,
    )
    db_session.add(existing_book)
    db_session.commit()
    db_session.refresh(existing_book)

    existing_book_id = existing_book.id

    def fake_get_google_book(external_id: str) -> BookSearchResult:
        assert external_id == "book-with-existing-genre"

        return BookSearchResult(
            external_id="book-with-existing-genre",
            title="Google Books側のタイトル",
            author="Google Books側の著者",
            isbn="9780000000014",
            genre=BookGenre.BUSINESS,
            cover_image_url=None,
        )

    monkeypatch.setattr(
        user_books,
        "get_google_book",
        fake_get_google_book,
    )

    response = client.post(
        "/users/me/books/from-search",
        json={
            "external_id": "book-with-existing-genre",
            "priority": "medium",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["book_id"] == existing_book_id

    saved_user_book = db_session.get(UserBook, response_data["id"])
    assert saved_user_book is not None

    db_session.refresh(existing_book)
    assert existing_book.genre == BookGenre.HUMANITIES

    db_session.delete(saved_user_book)
    db_session.flush()
    db_session.delete(existing_book)
    db_session.commit()


@pytest.mark.parametrize("isbn", ["9780000000013", None])
def test_create_user_book_from_search_returns_conflict_for_duplicate(
    monkeypatch,
    access_token,
    db_session,
    registered_user,
    isbn,
):
    def fake_get_google_book(external_id: str) -> BookSearchResult:
        assert external_id == "duplicate-book-id"

        return BookSearchResult(
            external_id="duplicate-book-id",
            title="重複確認用の本",
            author="重複確認用の著者",
            isbn=isbn,
            genre=BookGenre.MANGA,
            cover_image_url=None,
        )

    monkeypatch.setattr(
        user_books,
        "get_google_book",
        fake_get_google_book,
    )

    request_data = {
        "external_id": "duplicate-book-id",
        "priority": "high",
    }

    first_response = client.post(
        "/users/me/books/from-search",
        json=request_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert first_response.status_code == 201
    first_response_data = first_response.json()

    second_response = client.post(
        "/users/me/books/from-search",
        json=request_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "この本は既に読みたいリストへ登録されています。"
    }

    saved_books = db_session.scalars(
        select(Book).where(Book.external_id == "duplicate-book-id")
    ).all()
    saved_user_books = db_session.scalars(
        select(UserBook).where(
            UserBook.user_id == registered_user.id,
            UserBook.book_id == first_response_data["book_id"],
        )
    ).all()

    assert len(saved_books) == 1
    assert saved_books[0].isbn == isbn
    assert len(saved_user_books) == 1
    assert saved_books[0].genre == BookGenre.MANGA
    assert saved_user_books[0].book_id == first_response_data["book_id"]

    db_session.delete(saved_user_books[0])
    db_session.flush()
    db_session.delete(saved_books[0])
    db_session.commit()


def test_create_user_book_from_search_unauthorized_without_token():
    response = client.post(
        "/users/me/books/from-search",
        json={
            "external_id": "abc123",
            "priority": "high",
        },
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "request_data",
    [
        {
            "external_id": "",
            "priority": "high",
        },
        {
            "external_id": "   ",
            "priority": "high",
        },
        {
            "external_id": "abc123",
            "priority": "urgent",
        },
    ],
)
def test_create_user_book_from_search_rejects_invalid_request(
    request_data,
    access_token,
):
    response = client.post(
        "/users/me/books/from-search",
        json=request_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422


def test_create_user_book_from_search_rejects_incomplete_google_book(
    monkeypatch,
    access_token,
):
    def fake_get_google_book(external_id: str) -> None:
        assert external_id == "abc123"

    monkeypatch.setattr(
        user_books,
        "get_google_book",
        fake_get_google_book,
    )

    response = client.post(
        "/users/me/books/from-search",
        json={
            "external_id": "abc123",
            "priority": "high",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "選択した本には登録に必要な書籍情報がありません。"
    }


def test_create_user_book_from_search_returns_not_found_for_missing_google_book(
    monkeypatch,
    access_token,
):
    def fake_get_google_book(external_id: str) -> None:
        assert external_id == "missing-book-id"

        request = httpx2.Request(
            "GET",
            f"https://www.googleapis.com/books/v1/volumes/{external_id}",
        )
        google_response = httpx2.Response(
            status_code=404,
            request=request,
        )

        raise httpx2.HTTPStatusError(
            "Google Books API returned 404",
            request=request,
            response=google_response,
        )

    monkeypatch.setattr(
        user_books,
        "get_google_book",
        fake_get_google_book,
    )

    response = client.post(
        "/users/me/books/from-search",
        json={
            "external_id": "missing-book-id",
            "priority": "high",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "選択した本がGoogle Booksに存在しません。"}


def test_create_user_book_from_search_returns_bad_gateway_for_google_error(
    monkeypatch,
    access_token,
):
    def fake_get_google_book(external_id: str) -> None:
        assert external_id == "error-book-id"

        request = httpx2.Request(
            "GET",
            f"https://www.googleapis.com/books/v1/volumes/{external_id}",
        )
        google_response = httpx2.Response(
            status_code=500,
            request=request,
        )

        raise httpx2.HTTPStatusError(
            "Google Books API returned 500",
            request=request,
            response=google_response,
        )

    monkeypatch.setattr(
        user_books,
        "get_google_book",
        fake_get_google_book,
    )

    response = client.post(
        "/users/me/books/from-search",
        json={
            "external_id": "error-book-id",
            "priority": "high",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 502
    assert response.json() == {
        "detail": "書籍検索サービスから正常な応答を取得できませんでした。"
    }


def test_create_user_book_from_search_returns_bad_gateway_for_connection_error(
    monkeypatch,
    access_token,
):
    def fake_get_google_book(external_id: str) -> None:
        assert external_id == "connection-error-book-id"

        request = httpx2.Request(
            "GET",
            f"https://www.googleapis.com/books/v1/volumes/{external_id}",
        )
        raise httpx2.RequestError(
            "Google Books API connection error",
            request=request,
        )

    monkeypatch.setattr(
        user_books,
        "get_google_book",
        fake_get_google_book,
    )

    response = client.post(
        "/users/me/books/from-search",
        json={
            "external_id": "connection-error-book-id",
            "priority": "high",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 502
    assert response.json() == {"detail": "書籍検索サービスへ接続できませんでした。"}


def test_create_user_book_from_search_returns_gateway_timeout(
    monkeypatch,
    access_token,
):
    def fake_get_google_book(external_id: str) -> None:
        assert external_id == "timeout-book-id"

        request = httpx2.Request(
            "GET",
            f"https://www.googleapis.com/books/v1/volumes/{external_id}",
        )
        raise httpx2.TimeoutException(
            "Google Books API timeout",
            request=request,
        )

    monkeypatch.setattr(
        user_books,
        "get_google_book",
        fake_get_google_book,
    )

    response = client.post(
        "/users/me/books/from-search",
        json={
            "external_id": "timeout-book-id",
            "priority": "high",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 504
    assert response.json() == {
        "detail": "書籍検索サービスから時間内に応答がありませんでした。"
    }


def test_update_completed_status_with_reading_post_returns_conflict(
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

    completed_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert completed_response.status_code == 200

    reading_post_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "学びが多い"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert reading_post_response.status_code == 201

    status_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "reading"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert status_response.status_code == 409

    user_book = db_session.get(UserBook, post_response_data["id"])
    assert user_book is not None
    assert user_book.status.value == "completed"
    assert user_book.recommendation_score == 5
    assert user_book.reading_post is not None


def test_delete_user_book_with_reading_post_returns_conflict(
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

    completed_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert completed_response.status_code == 200

    reading_post_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "学びが多い"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert reading_post_response.status_code == 201

    delete_response = client.delete(
        f"/users/me/books/{target_book_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert delete_response.status_code == 409

    user_book = db_session.get(UserBook, post_response_data["id"])
    assert user_book is not None
    assert user_book.reading_post is not None
    assert user_book.reading_post.id == reading_post_response.json()["id"]


@pytest.mark.parametrize("incoming_isbn", [None, "9780000000020"])
def test_create_user_book_from_search_reuses_external_id_before_isbn(
    monkeypatch,
    access_token,
    other_access_token,
    book_in_db,
    db_session,
    incoming_isbn,
):
    existing_book = db_session.get(Book, book_in_db.id)
    existing_book.external_id = "existing-no-isbn-book"
    db_session.commit()
    existing_book_id = book_in_db.id

    def fake_get_google_book(external_id: str) -> BookSearchResult:
        assert external_id == "existing-no-isbn-book"
        return BookSearchResult(
            external_id=external_id,
            title="Google側のタイトル",
            author="Google側の著者",
            isbn=incoming_isbn,
            genre=BookGenre.OTHER,
            cover_image_url=None,
        )

    monkeypatch.setattr(user_books, "get_google_book", fake_get_google_book)

    try:
        first_response = client.post(
            "/users/me/books/from-search",
            json={"external_id": "existing-no-isbn-book", "priority": "high"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        second_response = client.post(
            "/users/me/books/from-search",
            json={"external_id": "existing-no-isbn-book", "priority": "medium"},
            headers={"Authorization": f"Bearer {other_access_token}"},
        )

        assert first_response.status_code == 201
        assert second_response.status_code == 201
        assert first_response.json()["book_id"] == existing_book_id
        assert second_response.json()["book_id"] == existing_book_id
        assert first_response.json()["id"] != second_response.json()["id"]
        assert db_session.scalars(
            select(Book.id).where(Book.external_id == "existing-no-isbn-book")
        ).all() == [existing_book_id]
    finally:
        for saved_user_book in db_session.scalars(
            select(UserBook).where(UserBook.book_id == existing_book_id)
        ).all():
            db_session.delete(saved_user_book)
        db_session.commit()
