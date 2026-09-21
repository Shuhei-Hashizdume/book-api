import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from main import app
from models import ReadingPost, UserBook

client = TestClient(app)


def test_create_reading_post(user_book_data, access_token, db_session):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert post_response.status_code == 201
    post_response_data = post_response.json()
    target_book_id = post_response.json()["book_id"]

    patch_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert patch_response.status_code == 200

    create_reading_post_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "学びが多い"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_reading_post_response.status_code == 201
    create_reading_post_response_data = create_reading_post_response.json()

    assert create_reading_post_response_data["recommendation_reason"] == "学びが多い"
    assert create_reading_post_response_data["is_public"] is True
    assert isinstance(create_reading_post_response_data["id"], int)
    assert create_reading_post_response_data["created_at"] is not None

    reading_post = db_session.get(ReadingPost, create_reading_post_response_data["id"])
    assert reading_post is not None

    assert reading_post.user_book_id == post_response_data["id"]
    assert reading_post.recommendation_reason == "学びが多い"
    assert reading_post.is_public is True
    assert reading_post.created_at is not None


def test_get_reading_post(user_book_data, access_token):
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

    create_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "GETで取得するおすすめ理由"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_response.status_code == 201

    get_response = client.get(
        f"/users/me/books/{target_book_id}/reading-post",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert get_response.status_code == 200
    assert get_response.json() == create_response.json()


def test_get_reading_post_without_user_book_returns_not_found(book_in_db, access_token):
    response = client.get(
        f"/users/me/books/{book_in_db.id}/reading-post",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404


def test_get_reading_post_without_reading_post_returns_not_found(
    user_book_data, access_token
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    response = client.get(
        f"/users/me/books/{target_book_id}/reading-post",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404


def test_get_reading_post_unauthorized_without_token(book_in_db):
    response = client.get(
        f"/users/me/books/{book_in_db.id}/reading-post",
    )

    assert response.status_code == 401


def test_get_other_users_reading_post_returns_not_found(
    user_book_data, access_token, other_access_token
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

    create_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "本人だけが取得できる投稿"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_response.status_code == 201

    response = client.get(
        f"/users/me/books/{target_book_id}/reading-post",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert response.status_code == 404


def test_update_reading_post(user_book_data, access_token, db_session):
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

    create_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "更新前のおすすめ理由", "is_public": False},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_response.status_code == 201
    created_post = create_response.json()

    update_response = client.patch(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "更新後のおすすめ理由"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert update_response.status_code == 200
    updated_post = update_response.json()
    assert updated_post["recommendation_reason"] == "更新後のおすすめ理由"
    assert updated_post["id"] == created_post["id"]
    assert updated_post["is_public"] == created_post["is_public"]
    assert updated_post["created_at"] == created_post["created_at"]

    reading_post = db_session.get(ReadingPost, created_post["id"])
    assert reading_post is not None
    assert reading_post.recommendation_reason == "更新後のおすすめ理由"
    assert reading_post.is_public is False


def test_update_reading_post_without_reading_post_returns_not_found(
    user_book_data, access_token
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    response = client.patch(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "更新後のおすすめ理由"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404


def test_update_reading_post_unauthorized_without_token(book_in_db):
    response = client.patch(
        f"/users/me/books/{book_in_db.id}/reading-post",
        json={"recommendation_reason": "更新後のおすすめ理由"},
    )

    assert response.status_code == 401


def test_update_other_users_reading_post_returns_not_found(
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

    create_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "所有者本人のおすすめ理由"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_response.status_code == 201
    created_post = create_response.json()

    response = client.patch(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "他人が変更したおすすめ理由"},
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert response.status_code == 404

    reading_post = db_session.get(ReadingPost, created_post["id"])
    assert reading_post is not None
    assert reading_post.recommendation_reason == "所有者本人のおすすめ理由"


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"recommendation_reason": None},
        {"recommendation_reason": ""},
        {"recommendation_reason": "   "},
        {"recommendation_reason": "あ" * 1001},
    ],
)
def test_update_reading_post_rejects_invalid_recommendation_reason(
    book_in_db, access_token, payload
):
    response = client.patch(
        f"/users/me/books/{book_in_db.id}/reading-post",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422


def test_delete_reading_post(user_book_data, access_token, db_session):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    user_book_id = user_book_response.json()["id"]
    target_book_id = user_book_response.json()["book_id"]

    status_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert status_response.status_code == 200

    create_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "削除対象のおすすめ理由"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_response.status_code == 201
    reading_post_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/users/me/books/{target_book_id}/reading-post",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert db_session.get(ReadingPost, reading_post_id) is None
    assert db_session.get(UserBook, user_book_id) is not None


def test_delete_reading_post_without_user_book_returns_not_found(
    book_in_db, access_token
):
    response = client.delete(
        f"/users/me/books/{book_in_db.id}/reading-post",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404


def test_delete_reading_post_without_reading_post_returns_not_found(
    user_book_data, access_token
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    response = client.delete(
        f"/users/me/books/{target_book_id}/reading-post",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404


def test_delete_reading_post_unauthorized_without_token(book_in_db):
    response = client.delete(
        f"/users/me/books/{book_in_db.id}/reading-post",
    )

    assert response.status_code == 401


def test_delete_other_users_reading_post_returns_not_found(
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

    create_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "所有者本人のおすすめ理由"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_response.status_code == 201
    reading_post_id = create_response.json()["id"]

    response = client.delete(
        f"/users/me/books/{target_book_id}/reading-post",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert response.status_code == 404
    assert db_session.get(ReadingPost, reading_post_id) is not None


def test_delete_reading_post_allows_user_book_status_change_and_deletion(
    user_book_data, access_token, db_session
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    user_book_id = user_book_response.json()["id"]
    target_book_id = user_book_response.json()["book_id"]

    completed_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert completed_response.status_code == 200

    create_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "削除後の操作を確認する投稿"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_response.status_code == 201

    delete_post_response = client.delete(
        f"/users/me/books/{target_book_id}/reading-post",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert delete_post_response.status_code == 204

    status_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "reading"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert status_response.status_code == 200
    assert status_response.json()["status"] == "reading"

    delete_user_book_response = client.delete(
        f"/users/me/books/{target_book_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert delete_user_book_response.status_code == 204
    assert db_session.get(UserBook, user_book_id) is None


def test_create_private_reading_post(user_book_data, access_token, db_session):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert post_response.status_code == 201
    post_response_data = post_response.json()
    target_book_id = post_response_data["book_id"]

    patch_response = client.patch(
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert patch_response.status_code == 200

    create_reading_post_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "非公開のおすすめ理由", "is_public": False},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_reading_post_response.status_code == 201
    create_reading_post_response_data = create_reading_post_response.json()
    assert create_reading_post_response_data["is_public"] is False

    reading_post = db_session.get(ReadingPost, create_reading_post_response_data["id"])
    assert reading_post is not None
    assert reading_post.is_public is False


def test_create_reading_post_before_completed_returns_conflict(
    user_book_data, access_token, db_session
):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert post_response.status_code == 201
    post_response_data = post_response.json()

    create_reading_post_response = client.post(
        f"/users/me/books/{post_response_data['book_id']}/reading-post",
        json={"recommendation_reason": "学びが多い"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_reading_post_response.status_code == 409

    user_book = db_session.get(UserBook, post_response_data["id"])
    assert user_book is not None
    assert user_book.reading_post is None


def test_create_duplicate_reading_post_returns_conflict(
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
        f"/users/me/books/{target_book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert patch_response.status_code == 200

    first_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "最初のおすすめ理由"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert first_response.status_code == 201

    second_response = client.post(
        f"/users/me/books/{target_book_id}/reading-post",
        json={"recommendation_reason": "2件目のおすすめ理由"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert second_response.status_code == 409

    user_book = db_session.get(UserBook, post_response_data["id"])
    assert user_book is not None
    assert user_book.reading_post is not None
    assert user_book.reading_post.id == first_response.json()["id"]
    assert user_book.reading_post.recommendation_reason == "最初のおすすめ理由"


def test_create_reading_post_returns_conflict_when_database_rejects_duplicate(
    user_book_data, access_token, monkeypatch
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

    rollback_was_called = False
    original_rollback = Session.rollback

    def raise_duplicate_error(_session):
        raise IntegrityError("INSERT INTO reading_posts", {}, Exception("duplicate"))

    def record_rollback(session):
        nonlocal rollback_was_called
        rollback_was_called = True
        return original_rollback(session)

    with monkeypatch.context() as patch:
        patch.setattr(Session, "commit", raise_duplicate_error)
        patch.setattr(Session, "rollback", record_rollback)

        response = client.post(
            f"/users/me/books/{target_book_id}/reading-post",
            json={"recommendation_reason": "同時登録を想定したおすすめ理由"},
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert response.status_code == 409
    assert rollback_was_called is True


def test_create_reading_post_without_user_book_returns_not_found(
    book_in_db, access_token
):
    response = client.post(
        f"/users/me/books/{book_in_db.id}/reading-post",
        json={"recommendation_reason": "学びが多い"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404


def test_create_reading_post_unauthorized_without_token(book_in_db):
    response = client.post(
        f"/users/me/books/{book_in_db.id}/reading-post",
        json={"recommendation_reason": "学びが多い"},
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"recommendation_reason": None},
        {"recommendation_reason": ""},
        {"recommendation_reason": "   "},
        {"recommendation_reason": "あ" * 1001},
    ],
)
def test_create_reading_post_rejects_invalid_recommendation_reason(
    book_in_db, access_token, payload
):
    response = client.post(
        f"/users/me/books/{book_in_db.id}/reading-post",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422
