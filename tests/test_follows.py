import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from main import app
from models import Follow, User
from security import create_access_token

client = TestClient(app)


def test_create_follow(access_token, db_session, other_user, registered_user):
    response = client.post(
        f"/users/{other_user.id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 201
    response_data = response.json()
    assert isinstance(response_data["id"], int)
    assert response_data["follower_id"] == registered_user.id
    assert response_data["followed_id"] == other_user.id
    assert response_data["created_at"] is not None

    follow = db_session.get(Follow, response_data["id"])
    assert follow is not None
    assert follow.follower_id == registered_user.id
    assert follow.followed_id == other_user.id


def test_create_follow_returns_not_found_for_missing_user(
    access_token, registered_user, db_session
):
    missing_user_id = 999999

    response = client.post(
        f"/users/{missing_user_id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404

    statement = select(Follow).where(
        Follow.follower_id == registered_user.id,
        Follow.followed_id == missing_user_id,
    )
    assert db_session.scalar(statement) is None


def test_create_follow_for_self_returns_conflict(
    access_token, registered_user, db_session
):
    response = client.post(
        f"/users/{registered_user.id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 409

    statement = select(Follow).where(
        Follow.follower_id == registered_user.id,
        Follow.followed_id == registered_user.id,
    )
    assert db_session.scalar(statement) is None


def test_create_duplicate_follow_returns_conflict(
    access_token, registered_user, other_user, db_session
):
    first_response = client.post(
        f"/users/{other_user.id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert first_response.status_code == 201

    second_response = client.post(
        f"/users/{other_user.id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert second_response.status_code == 409

    statement = select(Follow).where(
        Follow.follower_id == registered_user.id,
        Follow.followed_id == other_user.id,
    )
    follows = db_session.scalars(statement).all()
    assert len(follows) == 1
    assert follows[0].id == first_response.json()["id"]


def test_create_follow_unauthorized_without_token(other_user, db_session):
    response = client.post(f"/users/{other_user.id}/follow")

    assert response.status_code == 401

    statement = select(Follow).where(Follow.followed_id == other_user.id)
    assert db_session.scalar(statement) is None


def test_create_follow_returns_conflict_when_database_rejects_duplicate(
    access_token, registered_user, other_user, db_session, monkeypatch
):
    rollback_was_called = False
    original_rollback = Session.rollback

    def raise_duplicate_error(_session):
        raise IntegrityError("INSERT INTO follows", {}, Exception("duplicate"))

    def record_rollback(session):
        nonlocal rollback_was_called
        rollback_was_called = True
        return original_rollback(session)

    with monkeypatch.context() as patch:
        patch.setattr(Session, "commit", raise_duplicate_error)
        patch.setattr(Session, "rollback", record_rollback)

        response = client.post(
            f"/users/{other_user.id}/follow",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert response.status_code == 409
    assert rollback_was_called is True

    statement = select(Follow).where(
        Follow.follower_id == registered_user.id,
        Follow.followed_id == other_user.id,
    )
    assert db_session.scalar(statement) is None


def test_delete_follow(access_token, other_user, db_session):
    create_response = client.post(
        f"/users/{other_user.id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_response.status_code == 201
    follow_id = create_response.json()["id"]
    followed_user_id = other_user.id

    delete_response = client.delete(
        f"/users/{followed_user_id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert db_session.get(Follow, follow_id) is None
    assert db_session.get(User, followed_user_id) is not None


def test_delete_follow_returns_not_found_for_missing_user(access_token, db_session):
    missing_user_id = 999999

    response = client.delete(
        f"/users/{missing_user_id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404

    statement = select(Follow).where(Follow.followed_id == missing_user_id)
    assert db_session.scalar(statement) is None


def test_delete_follow_returns_not_found_without_follow(
    access_token, registered_user, other_user, db_session
):
    response = client.delete(
        f"/users/{other_user.id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404

    statement = select(Follow).where(
        Follow.follower_id == registered_user.id,
        Follow.followed_id == other_user.id,
    )
    assert db_session.scalar(statement) is None
    assert db_session.get(User, other_user.id) is not None


def test_delete_follow_unauthorized_without_token(other_user, db_session):
    response = client.delete(f"/users/{other_user.id}/follow")

    assert response.status_code == 401

    statement = select(Follow).where(Follow.followed_id == other_user.id)
    assert db_session.scalar(statement) is None
    assert db_session.get(User, other_user.id) is not None


def test_delete_follow_does_not_delete_another_users_follow(
    access_token,
    registered_user,
    other_access_token,
    third_user,
    db_session,
):
    create_response = client.post(
        f"/users/{third_user.id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_response.status_code == 201
    follow_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/users/{third_user.id}/follow",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert delete_response.status_code == 404

    follow = db_session.get(Follow, follow_id)
    assert follow is not None
    assert follow.follower_id == registered_user.id
    assert follow.followed_id == third_user.id


def test_delete_follower_user_cascades_to_follow(
    access_token, registered_user, other_user, db_session
):
    create_response = client.post(
        f"/users/{other_user.id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_response.status_code == 201
    follow_id = create_response.json()["id"]
    follower_id = registered_user.id
    followed_user_id = other_user.id

    db_session.delete(registered_user)
    db_session.commit()

    assert db_session.get(User, follower_id) is None
    assert db_session.get(Follow, follow_id) is None
    assert db_session.get(User, followed_user_id) is not None


def test_delete_followed_user_cascades_to_follow(
    other_access_token, other_user, registered_user, db_session
):
    create_response = client.post(
        f"/users/{registered_user.id}/follow",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert create_response.status_code == 201
    follow_id = create_response.json()["id"]
    follower_id = other_user.id
    followed_user_id = registered_user.id

    db_session.delete(registered_user)
    db_session.commit()

    assert db_session.get(User, followed_user_id) is None
    assert db_session.get(Follow, follow_id) is None
    assert db_session.get(User, follower_id) is not None


def test_follow_relationships(access_token, registered_user, other_user, db_session):
    create_response = client.post(
        f"/users/{other_user.id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_response.status_code == 201
    follow_id = create_response.json()["id"]
    follower_id = registered_user.id
    followed_user_id = other_user.id

    db_session.expire_all()

    follower = db_session.get(User, follower_id)
    followed = db_session.get(User, followed_user_id)
    follow = db_session.get(Follow, follow_id)

    assert follower is not None
    assert followed is not None
    assert follow is not None
    assert {item.id for item in follower.following_relationships} == {follow_id}
    assert {item.id for item in followed.follower_relationships} == {follow_id}
    assert follow.follower.id == follower_id
    assert follow.followed.id == followed_user_id


def test_database_rejects_following_self(registered_user, db_session):
    follow = Follow(
        follower_id=registered_user.id,
        followed_id=registered_user.id,
    )
    db_session.add(follow)

    with pytest.raises(IntegrityError) as error_info:
        db_session.commit()

    assert "ck_follows_different_users" in str(error_info.value.orig)

    db_session.rollback()

    statement = select(Follow).where(
        Follow.follower_id == registered_user.id,
        Follow.followed_id == registered_user.id,
    )
    assert db_session.scalar(statement) is None


def test_same_user_can_follow_different_users(
    access_token, registered_user, other_user, third_user, db_session
):
    first_response = client.post(
        f"/users/{other_user.id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    second_response = client.post(
        f"/users/{third_user.id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert first_response.json()["id"] != second_response.json()["id"]

    statement = select(Follow).where(Follow.follower_id == registered_user.id)
    follows = db_session.scalars(statement).all()
    assert len(follows) == 2
    assert {follow.followed_id for follow in follows} == {
        other_user.id,
        third_user.id,
    }


def test_different_users_can_follow_same_user(
    access_token,
    registered_user,
    other_user,
    other_access_token,
    third_user,
    db_session,
):
    first_response = client.post(
        f"/users/{third_user.id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    second_response = client.post(
        f"/users/{third_user.id}/follow",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert first_response.json()["id"] != second_response.json()["id"]

    statement = select(Follow).where(Follow.followed_id == third_user.id)
    follows = db_session.scalars(statement).all()
    assert len(follows) == 2
    assert {follow.follower_id for follow in follows} == {
        registered_user.id,
        other_user.id,
    }


def test_list_following_users(access_token, other_user, third_user):

    first_following_user_response = client.post(
        f"/users/{other_user.id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    second_following_user_response = client.post(
        f"/users/{third_user.id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert first_following_user_response.status_code == 201
    assert second_following_user_response.status_code == 201

    response = client.get(
        "/users/me/following", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2
    assert {(item["id"], item["username"]) for item in response_data} == {
        (other_user.id, other_user.username),
        (third_user.id, third_user.username),
    }


def test_list_following_users_returns_empty_list(access_token):
    response = client.get(
        "/users/me/following", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 0
    assert response_data == []


def test_list_following_users_returns_without_access_token_error():
    response = client.get("/users/me/following")

    assert response.status_code == 401


def test_list_following_users_excludes_other_users_following(
    access_token, registered_user, other_access_token, third_user
):
    create_own_follow_response = client.post(
        f"/users/{third_user.id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_own_follow_response.status_code == 201

    create_other_follow_response = client.post(
        f"/users/{registered_user.id}/follow",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )
    assert create_other_follow_response.status_code == 201

    response = client.get(
        "/users/me/following",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == [{"id": third_user.id, "username": third_user.username}]


def test_list_follower_users(
    access_token, other_access_token, other_user, third_user, registered_user
):
    third_access_token = create_access_token(third_user.id)

    first_following_user_response = client.post(
        f"/users/{registered_user.id}/follow",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )
    second_following_user_response = client.post(
        f"/users/{registered_user.id}/follow",
        headers={"Authorization": f"Bearer {third_access_token}"},
    )

    assert first_following_user_response.status_code == 201
    assert second_following_user_response.status_code == 201

    response = client.get(
        "/users/me/followers",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2
    assert {(item["id"], item["username"]) for item in response_data} == {
        (other_user.id, other_user.username),
        (third_user.id, third_user.username),
    }


def test_list_follower_users_returns_without_access_token_error():
    response = client.get("/users/me/followers")

    assert response.status_code == 401


def test_list_follower_users_excludes_other_users_followers(
    access_token, registered_user, other_user, other_access_token, third_user
):
    create_own_follower_response = client.post(
        f"/users/{registered_user.id}/follow",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )
    assert create_own_follower_response.status_code == 201

    create_other_follower_response = client.post(
        f"/users/{third_user.id}/follow",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_other_follower_response.status_code == 201

    response = client.get(
        "/users/me/followers",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == [
        {"id": other_user.id, "username": other_user.username}
    ]


def test_list_follower_users_returns_empty_list(access_token):
    response = client.get(
        "/users/me/followers",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == []
