from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select

from enums import ReadingPriority, ReadingStatus
from main import app
from models import Book, BookRating, CompletedBook, Follow, ReadingPost, UserBook

client = TestClient(app)


def test_read_user_profile(registered_user, other_user, book_in_db, db_session):
    registered_user.bio = "宜しくお願いします。"

    book = db_session.get(Book, book_in_db.id)
    assert book is not None
    book.cover_image_url = "https://example.com/public-bookshelf-cover.jpg"

    user_book = UserBook(
        user_id=registered_user.id,
        book_id=book_in_db.id,
        priority=ReadingPriority.HIGH,
        status=ReadingStatus.COMPLETED,
    )
    book_rating = BookRating(
        user_id=registered_user.id,
        book_id=book_in_db.id,
        recommendation_score=5,
    )
    completed_book = CompletedBook(
        user_id=registered_user.id,
        book_id=book_in_db.id,
    )

    reading_post = ReadingPost(
        user_id=registered_user.id,
        book_id=book_in_db.id,
        recommendation_score=book_rating.recommendation_score,
        recommendation_reason="テスト用のおすすめ理由",
        is_public=True,
    )
    follow = Follow(
        follower_id=other_user.id,
        followed_id=registered_user.id,
    )
    db_session.add_all([user_book, book_rating, completed_book, reading_post, follow])
    db_session.commit()
    db_session.refresh(reading_post)

    try:
        response = client.get(f"/users/{registered_user.id}/profile")

        assert response.status_code == 200
        response_data = response.json()

        assert response_data["id"] == registered_user.id
        assert response_data["username"] == registered_user.username
        assert response_data["bio"] == "宜しくお願いします。"
        assert response_data["completed_book_count"] == 1
        assert response_data["follower_count"] == 1
        assert len(response_data["public_books"]) == 1

        public_book = response_data["public_books"][0]
        assert public_book["book_id"] == book_in_db.id
        assert public_book["reading_post_id"] == reading_post.id
        assert public_book["title"] == book_in_db.title
        assert public_book["author"] == book_in_db.author
        assert public_book["genre"] == book_in_db.genre.value
        assert (
            public_book["cover_image_url"]
            == "https://example.com/public-bookshelf-cover.jpg"
        )
        assert public_book["recommendation_score"] == 5
        assert public_book["recommendation_reason"] == "テスト用のおすすめ理由"
    finally:
        db_session.delete(reading_post)
        db_session.flush()
        db_session.delete(user_book)
        db_session.delete(book_rating)
        db_session.delete(completed_book)
        db_session.delete(follow)
        db_session.commit()


def test_read_user_profile_returns_not_found_for_missing_user():
    response = client.get("/users/999999/profile")

    assert response.status_code == 404
    assert response.json() == {"detail": "ユーザーが見つかりません。"}


def test_read_user_profile_returns_empty_values(registered_user):
    response = client.get(f"/users/{registered_user.id}/profile")

    assert response.status_code == 200
    assert response.json() == {
        "id": registered_user.id,
        "username": registered_user.username,
        "bio": None,
        "completed_book_count": 0,
        "follower_count": 0,
        "public_books": [],
    }


def test_read_user_profile_excludes_private_reading_post(
    registered_user, book_in_db, db_session
):
    user_book = UserBook(
        user_id=registered_user.id,
        book_id=book_in_db.id,
        priority=ReadingPriority.HIGH,
        status=ReadingStatus.COMPLETED,
    )
    book_rating = BookRating(
        user_id=registered_user.id,
        book_id=book_in_db.id,
        recommendation_score=5,
    )
    completed_book = CompletedBook(
        user_id=registered_user.id,
        book_id=book_in_db.id,
    )

    reading_post = ReadingPost(
        user_id=registered_user.id,
        book_id=book_in_db.id,
        recommendation_score=book_rating.recommendation_score,
        recommendation_reason="非公開のおすすめ理由",
        is_public=False,
    )
    db_session.add_all([user_book, book_rating, completed_book, reading_post])
    db_session.commit()

    try:
        response = client.get(f"/users/{registered_user.id}/profile")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["completed_book_count"] == 1
        assert response_data["public_books"] == []
    finally:
        db_session.delete(reading_post)
        db_session.flush()
        db_session.delete(user_book)
        db_session.delete(book_rating)
        db_session.delete(completed_book)
        db_session.commit()


def test_read_user_profile_orders_public_books_by_newest_post(
    registered_user, book_in_db, db_session
):
    second_book = Book(
        title="2冊目のテスト本",
        author="2冊目のテスト著者",
        isbn=None,
    )
    db_session.add(second_book)
    db_session.commit()
    db_session.refresh(second_book)

    older_user_book = UserBook(
        user_id=registered_user.id,
        book_id=book_in_db.id,
        priority=ReadingPriority.HIGH,
        status=ReadingStatus.COMPLETED,
    )
    newer_user_book = UserBook(
        user_id=registered_user.id,
        book_id=second_book.id,
        priority=ReadingPriority.HIGH,
        status=ReadingStatus.COMPLETED,
    )
    older_book_rating = BookRating(
        user_id=registered_user.id,
        book_id=book_in_db.id,
        recommendation_score=4,
    )
    newer_book_rating = BookRating(
        user_id=registered_user.id,
        book_id=second_book.id,
        recommendation_score=5,
    )
    older_completed_book = CompletedBook(
        user_id=registered_user.id,
        book_id=book_in_db.id,
    )
    newer_completed_book = CompletedBook(
        user_id=registered_user.id,
        book_id=second_book.id,
    )

    older_post = ReadingPost(
        user_id=registered_user.id,
        book_id=book_in_db.id,
        recommendation_score=older_book_rating.recommendation_score,
        recommendation_reason="古い公開投稿",
        is_public=True,
        created_at=datetime(2026, 9, 24, tzinfo=timezone.utc),
    )
    newer_post = ReadingPost(
        user_id=registered_user.id,
        book_id=second_book.id,
        recommendation_score=newer_book_rating.recommendation_score,
        recommendation_reason="新しい公開投稿",
        is_public=True,
        created_at=datetime(2026, 9, 25, tzinfo=timezone.utc),
    )
    db_session.add_all(
        [
            older_user_book,
            newer_user_book,
            older_book_rating,
            newer_book_rating,
            older_completed_book,
            newer_completed_book,
            older_post,
            newer_post,
        ]
    )
    db_session.commit()
    db_session.refresh(older_post)
    db_session.refresh(newer_post)

    try:
        response = client.get(f"/users/{registered_user.id}/profile")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["completed_book_count"] == 2
        assert [book["reading_post_id"] for book in response_data["public_books"]] == [
            newer_post.id,
            older_post.id,
        ]
        assert [book["cover_image_url"] for book in response_data["public_books"]] == [
            None,
            None,
        ]
    finally:
        db_session.delete(newer_post)
        db_session.delete(older_post)
        db_session.flush()
        db_session.delete(newer_user_book)
        db_session.delete(older_user_book)
        db_session.delete(newer_book_rating)
        db_session.delete(older_book_rating)
        db_session.delete(newer_completed_book)
        db_session.delete(older_completed_book)
        db_session.flush()
        db_session.delete(second_book)
        db_session.commit()


def test_read_user_profile_preserves_completed_count_after_removing_user_book(
    registered_user, user_book_data, access_token, db_session
):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert post_response.status_code == 201
    book_id = post_response.json()["book_id"]

    patch_response = client.patch(
        f"/users/me/books/{book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert patch_response.status_code == 200

    delete_response = client.delete(
        f"/users/me/books/{book_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert delete_response.status_code == 204

    get_profile_response = client.get(
        f"/users/{registered_user.id}/profile",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert get_profile_response.status_code == 200
    get_profile_response_data = get_profile_response.json()
    assert get_profile_response_data["completed_book_count"] == 1

    complete_book_statement = select(CompletedBook).where(
        CompletedBook.user_id == registered_user.id, CompletedBook.book_id == book_id
    )
    complete_book = db_session.scalar(complete_book_statement)

    assert complete_book is not None


def test_read_user_profile_counts_same_book_only_once(
    registered_user, user_book_data, access_token, db_session
):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert post_response.status_code == 201
    book_id = post_response.json()["book_id"]

    first_completed_response = client.patch(
        f"/users/me/books/{book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert first_completed_response.status_code == 200

    reading_response = client.patch(
        f"/users/me/books/{book_id}/status",
        json={"status": "reading"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert reading_response.status_code == 200

    second_completed_response = client.patch(
        f"/users/me/books/{book_id}/status",
        json={"status": "completed", "recommendation_score": 4},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert second_completed_response.status_code == 200

    profile_response = client.get(f"/users/{registered_user.id}/profile")
    assert profile_response.status_code == 200
    assert profile_response.json()["completed_book_count"] == 1

    statement = select(CompletedBook).where(
        CompletedBook.user_id == registered_user.id,
        CompletedBook.book_id == book_id,
    )
    completed_books = db_session.scalars(statement).all()
    assert len(completed_books) == 1
