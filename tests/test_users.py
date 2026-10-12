from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from enums import ReadingPriority, ReadingStatus
from main import app
from models import (
    AISuggestion,
    Book,
    BookRating,
    CompletedBook,
    Follow,
    Insight,
    Like,
    ReadingPost,
    ReadingReminder,
    User,
    UserBook,
)
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


def test_delete_current_user(registered_user, access_token, db_session):
    user_id = registered_user.id

    delete_response = client.delete(
        "/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert delete_response.status_code == 204

    statement = select(User).where(User.id == user_id)
    user = db_session.scalar(statement)
    assert user is None


def test_delete_current_user_requires_access_token(registered_user, db_session):
    user_id = registered_user.id

    delete_response = client.delete("/users/me")
    assert delete_response.status_code == 401

    statement = select(User).where(User.id == user_id)
    assert db_session.scalar(statement) is not None


def test_read_current_user_rejects_access_token_after_account_deletion(
    access_token,
):
    delete_response = client.delete(
        "/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert delete_response.status_code == 204

    get_response = client.get(
        "/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert get_response.status_code == 401


def test_delete_current_user_deletes_user_book(
    registered_user, book_in_db, access_token, db_session
):
    user_id = registered_user.id
    book_id = book_in_db.id

    post_response = client.post(
        "/users/me/books",
        json={"book_id": book_id, "priority": "high"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert post_response.status_code == 201
    user_book_id = post_response.json()["id"]

    user_book_statement = select(UserBook).where(UserBook.id == user_book_id)
    assert db_session.scalar(user_book_statement) is not None

    delete_response = client.delete(
        "/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert delete_response.status_code == 204

    user_statement = select(User).where(User.id == user_id)
    assert db_session.scalar(user_statement) is None
    assert db_session.scalar(user_book_statement) is None

    book_statement = select(Book).where(Book.id == book_id)
    assert db_session.scalar(book_statement) is not None


def test_delete_current_user_deletes_insight_and_ai_suggestion(
    registered_user, book_in_db, access_token, db_session
):
    user_id = registered_user.id
    book_id = book_in_db.id

    insight = Insight(
        user_id=user_id,
        book_id=book_id,
        content="小さな挑戦を続けることが大切だと気づいた",
    )
    db_session.add(insight)
    db_session.commit()
    db_session.refresh(insight)
    insight_id = insight.id

    ai_suggestion = AISuggestion(
        insight_id=insight_id,
        clarified_insight="小さな挑戦を続ける",
        deep_dive="挑戦を続けることで経験を積める",
        practical_application="毎日取り組める小さな目標を決める",
        next_action="今日、小さな挑戦を1つ試す",
    )
    db_session.add(ai_suggestion)
    db_session.commit()
    db_session.refresh(ai_suggestion)
    ai_suggestion_id = ai_suggestion.id

    insight_statement = select(Insight).where(Insight.id == insight_id)
    ai_suggestion_statement = select(AISuggestion).where(
        AISuggestion.id == ai_suggestion_id
    )
    assert db_session.scalar(insight_statement) is not None
    assert db_session.scalar(ai_suggestion_statement) is not None

    delete_response = client.delete(
        "/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert delete_response.status_code == 204

    user_statement = select(User).where(User.id == user_id)
    assert db_session.scalar(user_statement) is None
    assert db_session.scalar(insight_statement) is None
    assert db_session.scalar(ai_suggestion_statement) is None

    book_statement = select(Book).where(Book.id == book_id)
    assert db_session.scalar(book_statement) is not None


def test_delete_current_user_deletes_book_rating_and_completed_book(
    registered_user, book_in_db, access_token, db_session
):
    user_id = registered_user.id
    book_id = book_in_db.id

    book_rating = BookRating(
        user_id=user_id,
        book_id=book_id,
        recommendation_score=5,
    )
    completed_book = CompletedBook(user_id=user_id, book_id=book_id)
    db_session.add_all([book_rating, completed_book])
    db_session.commit()

    book_rating_statement = select(BookRating).where(
        BookRating.user_id == user_id, BookRating.book_id == book_id
    )
    completed_book_statement = select(CompletedBook).where(
        CompletedBook.user_id == user_id, CompletedBook.book_id == book_id
    )
    assert db_session.scalar(book_rating_statement) is not None
    assert db_session.scalar(completed_book_statement) is not None

    delete_response = client.delete(
        "/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert delete_response.status_code == 204

    user_statement = select(User).where(User.id == user_id)
    assert db_session.scalar(user_statement) is None
    assert db_session.scalar(book_rating_statement) is None
    assert db_session.scalar(completed_book_statement) is None

    book_statement = select(Book).where(Book.id == book_id)
    assert db_session.scalar(book_statement) is not None


def test_delete_current_user_deletes_reading_post_and_its_likes(
    registered_user, other_user, book_in_db, access_token, db_session
):
    user_id = registered_user.id
    other_user_id = other_user.id
    book_id = book_in_db.id

    reading_post = ReadingPost(
        user_id=user_id,
        book_id=book_id,
        recommendation_score=5,
        recommendation_reason="日々の行動を見直すきっかけになったため",
        is_public=True,
    )
    db_session.add(reading_post)
    db_session.commit()
    db_session.refresh(reading_post)
    reading_post_id = reading_post.id

    like = Like(user_id=other_user_id, reading_post_id=reading_post_id)
    db_session.add(like)
    db_session.commit()
    db_session.refresh(like)
    like_id = like.id

    reading_post_statement = select(ReadingPost).where(
        ReadingPost.id == reading_post_id
    )
    like_statement = select(Like).where(Like.id == like_id)
    assert db_session.scalar(reading_post_statement) is not None
    assert db_session.scalar(like_statement) is not None

    delete_response = client.delete(
        "/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert delete_response.status_code == 204

    user_statement = select(User).where(User.id == user_id)
    assert db_session.scalar(user_statement) is None
    assert db_session.scalar(reading_post_statement) is None
    assert db_session.scalar(like_statement) is None

    other_user_statement = select(User).where(User.id == other_user_id)
    assert db_session.scalar(other_user_statement) is not None
    book_statement = select(Book).where(Book.id == book_id)
    assert db_session.scalar(book_statement) is not None


def test_delete_current_user_deletes_own_like_and_preserves_other_users_post(
    registered_user, other_user, book_in_db, access_token, db_session
):
    user_id = registered_user.id
    other_user_id = other_user.id
    book_id = book_in_db.id

    reading_post = ReadingPost(
        user_id=other_user_id,
        book_id=book_id,
        recommendation_score=5,
        recommendation_reason="日々の行動を見直すきっかけになったため",
        is_public=True,
    )
    db_session.add(reading_post)
    db_session.commit()
    db_session.refresh(reading_post)
    reading_post_id = reading_post.id

    like = Like(user_id=user_id, reading_post_id=reading_post_id)
    db_session.add(like)
    db_session.commit()
    db_session.refresh(like)
    like_id = like.id

    try:
        like_statement = select(Like).where(Like.id == like_id)
        assert db_session.scalar(like_statement) is not None

        delete_response = client.delete(
            "/users/me", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert delete_response.status_code == 204

        user_statement = select(User).where(User.id == user_id)
        assert db_session.scalar(user_statement) is None
        assert db_session.scalar(like_statement) is None

        reading_post_statement = select(ReadingPost).where(
            ReadingPost.id == reading_post_id
        )
        assert db_session.scalar(reading_post_statement) is not None
        other_user_statement = select(User).where(User.id == other_user_id)
        assert db_session.scalar(other_user_statement) is not None
        book_statement = select(Book).where(Book.id == book_id)
        assert db_session.scalar(book_statement) is not None
    finally:
        db_session.execute(delete(Like).where(Like.id == like_id))
        db_session.execute(delete(ReadingPost).where(ReadingPost.id == reading_post_id))
        db_session.commit()


def test_delete_current_user_deletes_follow_relationships(
    registered_user, other_user, access_token, db_session
):
    user_id = registered_user.id
    other_user_id = other_user.id

    following = Follow(follower_id=user_id, followed_id=other_user_id)
    follower = Follow(follower_id=other_user_id, followed_id=user_id)
    db_session.add_all([following, follower])
    db_session.commit()
    db_session.refresh(following)
    db_session.refresh(follower)
    following_id = following.id
    follower_id = follower.id

    following_statement = select(Follow).where(Follow.id == following_id)
    follower_statement = select(Follow).where(Follow.id == follower_id)
    assert db_session.scalar(following_statement) is not None
    assert db_session.scalar(follower_statement) is not None

    delete_response = client.delete(
        "/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert delete_response.status_code == 204

    user_statement = select(User).where(User.id == user_id)
    assert db_session.scalar(user_statement) is None
    assert db_session.scalar(following_statement) is None
    assert db_session.scalar(follower_statement) is None

    other_user_statement = select(User).where(User.id == other_user_id)
    assert db_session.scalar(other_user_statement) is not None


def test_delete_current_user_deletes_reading_reminder(
    registered_user, book_in_db, access_token, db_session
):
    user_id = registered_user.id
    book_id = book_in_db.id

    user_book = UserBook(
        user_id=user_id,
        book_id=book_id,
        priority=ReadingPriority.HIGH,
        status=ReadingStatus.READING,
    )
    db_session.add(user_book)
    db_session.commit()
    db_session.refresh(user_book)
    user_book_id = user_book.id

    reading_reminder = ReadingReminder(
        user_book_id=user_book_id,
        started_at=datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc),
        next_send_at=datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc),
    )
    db_session.add(reading_reminder)
    db_session.commit()
    db_session.refresh(reading_reminder)
    reading_reminder_id = reading_reminder.id

    user_book_statement = select(UserBook).where(UserBook.id == user_book_id)
    reading_reminder_statement = select(ReadingReminder).where(
        ReadingReminder.id == reading_reminder_id
    )
    assert db_session.scalar(user_book_statement) is not None
    assert db_session.scalar(reading_reminder_statement) is not None

    delete_response = client.delete(
        "/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert delete_response.status_code == 204

    user_statement = select(User).where(User.id == user_id)
    assert db_session.scalar(user_statement) is None
    assert db_session.scalar(user_book_statement) is None
    assert db_session.scalar(reading_reminder_statement) is None

    book_statement = select(Book).where(Book.id == book_id)
    assert db_session.scalar(book_statement) is not None


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


def test_database_rejects_bio_longer_than_160_characters(registered_user, db_session):
    registered_user.bio = "a" * 161

    with pytest.raises(IntegrityError) as error_info:
        db_session.commit()

    assert "ck_users_bio_range" in str(error_info.value.orig)
    db_session.rollback()
    db_session.refresh(registered_user)
    assert registered_user.bio is None


def test_database_rejects_blank_bio(registered_user, db_session):
    registered_user.bio = "   "

    with pytest.raises(IntegrityError) as error_info:
        db_session.commit()

    assert "ck_users_bio_not_blank" in str(error_info.value.orig)
    db_session.rollback()
    db_session.refresh(registered_user)
    assert registered_user.bio is None
