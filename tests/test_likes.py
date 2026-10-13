import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from main import app
from models import Like, ReadingPost, User
from security import create_access_token, hash_password

client = TestClient(app)


@pytest.mark.parametrize("reading_post_id", ["abc", 0, -1])
def test_create_like_rejects_invalid_post_id(reading_post_id, access_token):
    response = client.post(
        f"/reading-posts/{reading_post_id}/likes",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "reading_post_id"]


@pytest.mark.parametrize("reading_post_id", ["abc", 0, -1])
def test_delete_like_rejects_invalid_post_id(reading_post_id, access_token):
    response = client.delete(
        f"/reading-posts/{reading_post_id}/likes",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "reading_post_id"]


def test_create_like(
    user_book_data, access_token, other_user, other_access_token, db_session
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    status_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert status_response.status_code == 200

    reading_post_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "いいね対象の公開投稿"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert reading_post_response.status_code == 201
    reading_post_id = reading_post_response.json()["id"]

    like_response = client.post(
        f"/reading-posts/{reading_post_id}/likes",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert like_response.status_code == 201
    response_data = like_response.json()
    assert isinstance(response_data["id"], int)
    assert response_data["user_id"] == other_user.id
    assert response_data["reading_post_id"] == reading_post_id
    assert response_data["created_at"] is not None

    like = db_session.get(Like, response_data["id"])
    assert like is not None
    assert like.user_id == other_user.id
    assert like.reading_post_id == reading_post_id
    assert like.created_at is not None


def test_create_like_returns_not_found_for_missing_reading_post(
    access_token, db_session
):
    missing_reading_post_id = 999999

    response = client.post(
        f"/reading-posts/{missing_reading_post_id}/likes",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404

    statement = select(Like).where(
        Like.reading_post_id == missing_reading_post_id
    )
    assert db_session.scalar(statement) is None


def test_create_like_for_own_reading_post_returns_conflict(
    user_book_data, registered_user, access_token, db_session
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    status_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert status_response.status_code == 200

    reading_post_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "自分の公開投稿"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert reading_post_response.status_code == 201
    reading_post_id = reading_post_response.json()["id"]

    response = client.post(
        f"/reading-posts/{reading_post_id}/likes",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 409

    statement = select(Like).where(
        Like.user_id == registered_user.id,
        Like.reading_post_id == reading_post_id,
    )
    assert db_session.scalar(statement) is None


def test_create_duplicate_like_returns_conflict(
    user_book_data, access_token, other_user, other_access_token, db_session
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    status_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert status_response.status_code == 200

    reading_post_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "重複いいねの対象投稿"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert reading_post_response.status_code == 201
    reading_post_id = reading_post_response.json()["id"]

    first_response = client.post(
        f"/reading-posts/{reading_post_id}/likes",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert first_response.status_code == 201

    second_response = client.post(
        f"/reading-posts/{reading_post_id}/likes",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert second_response.status_code == 409

    statement = select(Like).where(
        Like.user_id == other_user.id,
        Like.reading_post_id == reading_post_id,
    )
    likes = db_session.scalars(statement).all()
    assert len(likes) == 1
    assert likes[0].id == first_response.json()["id"]


def test_create_like_for_private_reading_post_returns_not_found(
    user_book_data, access_token, other_user, other_access_token, db_session
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    status_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert status_response.status_code == 200

    reading_post_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={
            "recommendation_reason": "非公開の読了投稿",
            "is_public": False,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert reading_post_response.status_code == 201
    reading_post_id = reading_post_response.json()["id"]

    response = client.post(
        f"/reading-posts/{reading_post_id}/likes",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert response.status_code == 404

    statement = select(Like).where(
        Like.user_id == other_user.id,
        Like.reading_post_id == reading_post_id,
    )
    assert db_session.scalar(statement) is None


def test_create_like_unauthorized_without_token():
    response = client.post("/reading-posts/999999/likes")

    assert response.status_code == 401


def test_create_like_returns_conflict_when_database_rejects_duplicate(
    user_book_data,
    access_token,
    other_user,
    other_access_token,
    db_session,
    monkeypatch,
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    status_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert status_response.status_code == 200

    reading_post_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "DB制約違反を再現する公開投稿"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert reading_post_response.status_code == 201
    reading_post_id = reading_post_response.json()["id"]

    rollback_was_called = False
    original_rollback = Session.rollback

    def raise_duplicate_error(_session):
        raise IntegrityError("INSERT INTO likes", {}, Exception("duplicate"))

    def record_rollback(session):
        nonlocal rollback_was_called
        rollback_was_called = True
        return original_rollback(session)

    with monkeypatch.context() as patch:
        patch.setattr(Session, "commit", raise_duplicate_error)
        patch.setattr(Session, "rollback", record_rollback)

        response = client.post(
            f"/reading-posts/{reading_post_id}/likes",
            headers={"Authorization": f"Bearer {other_access_token}"},
        )

    assert response.status_code == 409
    assert rollback_was_called is True

    statement = select(Like).where(
        Like.user_id == other_user.id,
        Like.reading_post_id == reading_post_id,
    )
    assert db_session.scalar(statement) is None


def test_delete_like(
    user_book_data, access_token, other_access_token, db_session
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    status_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert status_response.status_code == 200

    reading_post_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "いいね解除対象の公開投稿"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert reading_post_response.status_code == 201
    reading_post_id = reading_post_response.json()["id"]

    like_response = client.post(
        f"/reading-posts/{reading_post_id}/likes",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert like_response.status_code == 201
    like_id = like_response.json()["id"]

    delete_response = client.delete(
        f"/reading-posts/{reading_post_id}/likes",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert db_session.get(Like, like_id) is None
    assert db_session.get(ReadingPost, reading_post_id) is not None


def test_delete_like_returns_not_found_for_missing_reading_post(access_token):
    response = client.delete(
        "/reading-posts/999999/likes",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404


def test_delete_like_returns_not_found_without_own_like(
    user_book_data, access_token, other_user, other_access_token, db_session
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    status_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert status_response.status_code == 200

    reading_post_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "未いいねの公開投稿"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert reading_post_response.status_code == 201
    reading_post_id = reading_post_response.json()["id"]

    response = client.delete(
        f"/reading-posts/{reading_post_id}/likes",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert response.status_code == 404

    statement = select(Like).where(
        Like.user_id == other_user.id,
        Like.reading_post_id == reading_post_id,
    )
    assert db_session.scalar(statement) is None


def test_delete_like_unauthorized_without_token():
    response = client.delete("/reading-posts/999999/likes")

    assert response.status_code == 401


def test_delete_like_for_private_reading_post_returns_not_found_and_keeps_like(
    user_book_data, access_token, other_access_token, db_session
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    status_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert status_response.status_code == 200

    reading_post_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "いいね後に非公開にする投稿"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert reading_post_response.status_code == 201
    reading_post_id = reading_post_response.json()["id"]

    like_response = client.post(
        f"/reading-posts/{reading_post_id}/likes",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert like_response.status_code == 201
    like_id = like_response.json()["id"]

    visibility_response = client.patch(
        f"/users/me/books/{target_book_id}/reading-post/visibility",
        json={"is_public": False},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert visibility_response.status_code == 200
    assert visibility_response.json()["is_public"] is False

    delete_response = client.delete(
        f"/reading-posts/{reading_post_id}/likes",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert delete_response.status_code == 404
    assert db_session.get(Like, like_id) is not None


def test_delete_like_does_not_delete_other_users_like(
    user_book_data,
    access_token,
    other_user,
    other_access_token,
    third_user,
    db_session,
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    status_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert status_response.status_code == 200

    reading_post_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "他人のいいねを保護する公開投稿"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert reading_post_response.status_code == 201
    reading_post_id = reading_post_response.json()["id"]

    like_response = client.post(
        f"/reading-posts/{reading_post_id}/likes",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert like_response.status_code == 201
    like_id = like_response.json()["id"]

    third_access_token = create_access_token(third_user.id)
    delete_response = client.delete(
        f"/reading-posts/{reading_post_id}/likes",
        headers={"Authorization": f"Bearer {third_access_token}"},
    )

    assert delete_response.status_code == 404

    like = db_session.get(Like, like_id)
    assert like is not None
    assert like.user_id == other_user.id
    assert like.reading_post_id == reading_post_id


def test_delete_reading_post_cascades_to_like(
    user_book_data, access_token, other_access_token, db_session
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    status_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert status_response.status_code == 200

    reading_post_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "CASCADE確認用の公開投稿"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert reading_post_response.status_code == 201
    reading_post_id = reading_post_response.json()["id"]

    like_response = client.post(
        f"/reading-posts/{reading_post_id}/likes",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert like_response.status_code == 201
    like_id = like_response.json()["id"]

    delete_response = client.delete(
        f"/users/me/books/{target_book_id}/reading-post",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert delete_response.status_code == 204
    assert db_session.get(ReadingPost, reading_post_id) is None
    assert db_session.get(Like, like_id) is None


def test_delete_user_cascades_to_like(user_book_data, access_token, db_session):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    status_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert status_response.status_code == 200

    reading_post_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "User削除CASCADE確認用の公開投稿"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert reading_post_response.status_code == 201
    reading_post_id = reading_post_response.json()["id"]

    liker = User(
        username="cascade-like-user",
        email="cascade-like@example.com",
        hashed_password=hash_password("cascade-like-password"),
    )
    db_session.add(liker)
    db_session.commit()
    db_session.refresh(liker)

    liker_id = liker.id
    liker_access_token = create_access_token(liker_id)
    like_response = client.post(
        f"/reading-posts/{reading_post_id}/likes",
        headers={"Authorization": f"Bearer {liker_access_token}"},
    )

    assert like_response.status_code == 201
    like_id = like_response.json()["id"]

    db_session.delete(liker)
    db_session.commit()

    assert db_session.get(User, liker_id) is None
    assert db_session.get(Like, like_id) is None
    assert db_session.get(ReadingPost, reading_post_id) is not None


def test_different_users_can_like_same_reading_post(
    user_book_data,
    access_token,
    other_user,
    other_access_token,
    third_user,
    db_session,
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    status_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert status_response.status_code == 200

    reading_post_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "2人がいいねする公開投稿"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert reading_post_response.status_code == 201
    reading_post_id = reading_post_response.json()["id"]

    first_response = client.post(
        f"/reading-posts/{reading_post_id}/likes",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert first_response.status_code == 201

    third_access_token = create_access_token(third_user.id)
    second_response = client.post(
        f"/reading-posts/{reading_post_id}/likes",
        headers={"Authorization": f"Bearer {third_access_token}"},
    )

    assert second_response.status_code == 201
    assert first_response.json()["id"] != second_response.json()["id"]

    statement = select(Like).where(Like.reading_post_id == reading_post_id)
    likes = db_session.scalars(statement).all()
    assert len(likes) == 2
    assert {like.user_id for like in likes} == {other_user.id, third_user.id}


def test_same_user_can_like_different_reading_posts(
    user_book_data,
    access_token,
    other_user,
    other_access_token,
    third_user,
    db_session,
):
    first_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert first_user_book_response.status_code == 201
    target_book_id = first_user_book_response.json()["book_id"]

    first_status_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert first_status_response.status_code == 200

    first_reading_post_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "1件目のいいね対象投稿"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert first_reading_post_response.status_code == 201
    first_reading_post_id = first_reading_post_response.json()["id"]

    third_access_token = create_access_token(third_user.id)
    second_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {third_access_token}"},
    )

    assert second_user_book_response.status_code == 201

    second_status_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 4},
        headers={"Authorization": f"Bearer {third_access_token}"},
    )

    assert second_status_response.status_code == 200

    second_reading_post_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "2件目のいいね対象投稿"},
        headers={"Authorization": f"Bearer {third_access_token}"},
    )

    assert second_reading_post_response.status_code == 201
    second_reading_post_id = second_reading_post_response.json()["id"]

    first_like_response = client.post(
        f"/reading-posts/{first_reading_post_id}/likes",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )
    second_like_response = client.post(
        f"/reading-posts/{second_reading_post_id}/likes",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert first_like_response.status_code == 201
    assert second_like_response.status_code == 201

    statement = select(Like).where(Like.user_id == other_user.id)
    likes = db_session.scalars(statement).all()
    assert len(likes) == 2
    assert {like.reading_post_id for like in likes} == {
        first_reading_post_id,
        second_reading_post_id,
    }

    cleanup_response = client.delete(
        f"/users/me/books/{target_book_id}/reading-post",
        headers={"Authorization": f"Bearer {third_access_token}"},
    )
    assert cleanup_response.status_code == 204
