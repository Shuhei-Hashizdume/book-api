from datetime import datetime, timezone

from fastapi.testclient import TestClient

from enums import ReadingPriority, ReadingStatus
from main import app
from models import Book, Follow, ReadingPost, UserBook

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
        recommendation_score=5,
    )
    db_session.add(user_book)
    db_session.commit()
    db_session.refresh(user_book)

    reading_post = ReadingPost(
        user_book_id=user_book.id,
        recommendation_reason="テスト用のおすすめ理由",
        is_public=True,
    )
    follow = Follow(
        follower_id=other_user.id,
        followed_id=registered_user.id,
    )
    db_session.add_all([reading_post, follow])
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
        recommendation_score=5,
    )
    db_session.add(user_book)
    db_session.commit()
    db_session.refresh(user_book)

    reading_post = ReadingPost(
        user_book_id=user_book.id,
        recommendation_reason="非公開のおすすめ理由",
        is_public=False,
    )
    db_session.add(reading_post)
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
        recommendation_score=4,
    )
    newer_user_book = UserBook(
        user_id=registered_user.id,
        book_id=second_book.id,
        priority=ReadingPriority.HIGH,
        status=ReadingStatus.COMPLETED,
        recommendation_score=5,
    )
    db_session.add_all([older_user_book, newer_user_book])
    db_session.commit()
    db_session.refresh(older_user_book)
    db_session.refresh(newer_user_book)

    older_post = ReadingPost(
        user_book_id=older_user_book.id,
        recommendation_reason="古い公開投稿",
        is_public=True,
        created_at=datetime(2026, 9, 24, tzinfo=timezone.utc),
    )
    newer_post = ReadingPost(
        user_book_id=newer_user_book.id,
        recommendation_reason="新しい公開投稿",
        is_public=True,
        created_at=datetime(2026, 9, 25, tzinfo=timezone.utc),
    )
    db_session.add_all([older_post, newer_post])
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
        db_session.flush()
        db_session.delete(second_book)
        db_session.commit()
