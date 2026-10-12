from fastapi.testclient import TestClient
from sqlalchemy import select

from main import app
from models import Insight, UserBook

client = TestClient(app)


def test_create_insight_for_other_users_book_returns_not_found(
    user_book_data, access_token, other_access_token
):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert post_response.status_code == 201
    target_book_id = post_response.json()["book_id"]

    post_insight_response = client.post(
        f"/users/me/books/{target_book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert post_insight_response.status_code == 404


def test_create_insight(
    user_book_data, access_token, registered_user, book_in_db, db_session
):
    post_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert post_response.status_code == 201
    target_book_id = post_response.json()["book_id"]

    post_insight_response = client.post(
        f"/users/me/books/{target_book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert post_insight_response.status_code == 201
    post_insight_response_data = post_insight_response.json()
    assert post_insight_response_data["content"] == "小さな挑戦が大事"
    assert isinstance(post_insight_response_data["id"], int)
    assert post_insight_response_data["book_id"] == target_book_id
    assert post_insight_response_data["book_title"] == book_in_db.title

    insight = db_session.get(Insight, post_insight_response_data["id"])
    assert insight is not None
    assert insight.user_id == registered_user.id
    assert insight.book_id == target_book_id
    assert insight.content == "小さな挑戦が大事"


def test_create_multiple_insights_for_same_book(
    user_book_data, access_token, registered_user, db_session
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    user_book_response_data = user_book_response.json()
    target_book_id = user_book_response_data["book_id"]

    first_response = client.post(
        f"/users/me/books/{target_book_id}/insights",
        json={"content": "最初の気づき"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    second_response = client.post(
        f"/users/me/books/{target_book_id}/insights",
        json={"content": "次の気づき"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    first_response_data = first_response.json()
    second_response_data = second_response.json()
    assert first_response_data["id"] != second_response_data["id"]

    first_insight = db_session.get(Insight, first_response_data["id"])
    second_insight = db_session.get(Insight, second_response_data["id"])

    assert first_insight is not None
    assert second_insight is not None
    assert first_insight.user_id == registered_user.id
    assert second_insight.user_id == registered_user.id
    assert first_insight.book_id == target_book_id
    assert second_insight.book_id == target_book_id


def test_insight_remains_after_deleting_user_book(
    user_book_data, access_token, registered_user, book_in_db, db_session
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert user_book_response.status_code == 201
    user_book_id = user_book_response.json()["id"]
    book_id = user_book_response.json()["book_id"]

    try:
        insight_response = client.post(
            f"/users/me/books/{book_id}/insights",
            json={"content": "本の登録を削除しても残したい気づき"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert insight_response.status_code == 201
        insight_id = insight_response.json()["id"]

        delete_response = client.delete(
            f"/users/me/books/{book_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert delete_response.status_code == 204
        assert db_session.get(UserBook, user_book_id) is None

        insight = db_session.get(Insight, insight_id)
        assert insight is not None
        assert insight.user_id == registered_user.id
        assert insight.book_id == book_id
        assert insight.content == "本の登録を削除しても残したい気づき"

        get_response = client.get(
            f"/users/me/books/{book_id}/insights",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert get_response.status_code == 200
        assert get_response.json() == [
            {
                "id": insight_id,
                "content": "本の登録を削除しても残したい気づき",
                "book_id": book_id,
                "book_title": book_in_db.title,
            }
        ]
    finally:
        db_session.rollback()
        insights = db_session.scalars(
            select(Insight).where(
                Insight.user_id == registered_user.id,
                Insight.book_id == book_id,
            )
        ).all()
        for insight in insights:
            db_session.delete(insight)
        db_session.commit()


def test_create_insight_rejects_blank_content(user_book_data, access_token):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    response = client.post(
        f"/users/me/books/{target_book_id}/insights",
        json={"content": "   "},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422


def test_create_insight_unauthorized_without_token(book_in_db):
    response = client.post(
        f"/users/me/books/{book_in_db.id}/insights",
        json={"content": "小さな挑戦が大事"},
    )

    assert response.status_code == 401


def test_list_insights_returns_multiple_insights_in_creation_order(
    user_book_data, access_token, book_in_db
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    first_response = client.post(
        f"/users/me/books/{target_book_id}/insights",
        json={"content": "最初の気づき"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    second_response = client.post(
        f"/users/me/books/{target_book_id}/insights",
        json={"content": "次の気づき"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    response = client.get(
        f"/users/me/books/{target_book_id}/insights",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2
    assert response_data[0]["content"] == "最初の気づき"
    assert response_data[1]["content"] == "次の気づき"
    assert response_data[0]["book_id"] == target_book_id
    assert response_data[1]["book_id"] == target_book_id
    assert response_data[0]["book_title"] == book_in_db.title
    assert response_data[1]["book_title"] == book_in_db.title


def test_list_insights_returns_empty_list(user_book_data, access_token):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    response = client.get(
        f"/users/me/books/{target_book_id}/insights",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_list_insights_returns_empty_list_without_user_book(book_in_db, access_token):
    response = client.get(
        f"/users/me/books/{book_in_db.id}/insights",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_list_insights_unauthorized_without_token(book_in_db):
    response = client.get(f"/users/me/books/{book_in_db.id}/insights")

    assert response.status_code == 401


def test_delete_insight(user_book_data, access_token, db_session):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    insight_response = client.post(
        f"/users/me/books/{target_book_id}/insights",
        json={"content": "削除確認用の気づき"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert insight_response.status_code == 201
    insight_id = insight_response.json()["id"]

    response = client.delete(
        f"/users/me/books/{target_book_id}/insights/{insight_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 204
    assert response.content == b""
    assert db_session.get(Insight, insight_id) is None


def test_delete_insight_after_deleting_user_book(
    user_book_data, access_token, db_session
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert user_book_response.status_code == 201
    book_id = user_book_response.json()["book_id"]

    insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "本の登録削除後に削除する気づき"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert insight_response.status_code == 201
    insight_id = insight_response.json()["id"]

    user_book_delete_response = client.delete(
        f"/users/me/books/{book_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert user_book_delete_response.status_code == 204

    insight_delete_response = client.delete(
        f"/users/me/books/{book_id}/insights/{insight_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert insight_delete_response.status_code == 204
    assert db_session.get(Insight, insight_id) is None

    get_response = client.get(
        f"/users/me/books/{book_id}/insights",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert get_response.status_code == 200
    assert get_response.json() == []


def test_delete_insight_not_found_without_user_book(book_in_db, access_token):
    response = client.delete(
        f"/users/me/books/{book_in_db.id}/insights/1",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404


def test_delete_other_users_insight(
    user_book_data,
    access_token,
    other_access_token,
    db_session,
):
    owner_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert owner_user_book_response.status_code == 201
    target_book_id = owner_user_book_response.json()["book_id"]

    other_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {other_access_token}"},
    )
    assert other_user_book_response.status_code == 201

    insight_response = client.post(
        f"/users/me/books/{target_book_id}/insights",
        json={"content": "所有者だけが削除できる気づき"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert insight_response.status_code == 201
    insight_id = insight_response.json()["id"]

    response = client.delete(
        f"/users/me/books/{target_book_id}/insights/{insight_id}",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert response.status_code == 404
    assert db_session.get(Insight, insight_id) is not None


def test_delete_insight_unauthorized_without_token(book_in_db):
    response = client.delete(
        f"/users/me/books/{book_in_db.id}/insights/1"
    )

    assert response.status_code == 401


def test_update_insight(
    user_book_data, access_token, registered_user, book_in_db, db_session
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert user_book_response.status_code == 201
    user_book_response_data = user_book_response.json()
    target_book_id = user_book_response_data["book_id"]

    insight_response = client.post(
        f"/users/me/books/{target_book_id}/insights",
        json={"content": "更新前の気づき"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert insight_response.status_code == 201
    insight_response_data = insight_response.json()
    insight_id = insight_response_data["id"]

    response = client.patch(
        f"/users/me/books/{target_book_id}/insights/{insight_id}",
        json={"content": "更新後の気づき"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == insight_id
    assert response_data["content"] == "更新後の気づき"
    assert response_data["book_id"] == target_book_id
    assert response_data["book_title"] == book_in_db.title

    insight = db_session.get(Insight, insight_id)
    assert insight is not None
    assert insight.content == "更新後の気づき"
    assert insight.user_id == registered_user.id
    assert insight.book_id == target_book_id


def test_update_insight_after_deleting_user_book(
    user_book_data, access_token, book_in_db
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert user_book_response.status_code == 201
    book_id = user_book_response.json()["book_id"]

    insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "更新前の気づき"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert insight_response.status_code == 201
    insight_id = insight_response.json()["id"]

    delete_response = client.delete(
        f"/users/me/books/{book_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert delete_response.status_code == 204

    update_response = client.patch(
        f"/users/me/books/{book_id}/insights/{insight_id}",
        json={"content": "本の登録削除後に更新した気づき"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["content"] == "本の登録削除後に更新した気づき"

    get_response = client.get(
        f"/users/me/books/{book_id}/insights",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert get_response.status_code == 200
    assert get_response.json() == [
        {
            "id": insight_id,
            "content": "本の登録削除後に更新した気づき",
            "book_id": book_id,
            "book_title": book_in_db.title,
        }
    ]


def test_update_insight_rejects_blank_content(
    user_book_data, access_token, db_session
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert user_book_response.status_code == 201
    target_book_id = user_book_response.json()["book_id"]

    insight_response = client.post(
        f"/users/me/books/{target_book_id}/insights",
        json={"content": "変更前の気づき"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert insight_response.status_code == 201
    insight_id = insight_response.json()["id"]

    response = client.patch(
        f"/users/me/books/{target_book_id}/insights/{insight_id}",
        json={"content": "   "},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422
    insight = db_session.get(Insight, insight_id)
    assert insight is not None
    assert insight.content == "変更前の気づき"


def test_update_insight_not_found_without_user_book(book_in_db, access_token):
    response = client.patch(
        f"/users/me/books/{book_in_db.id}/insights/1",
        json={"content": "変更後の気づき"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404


def test_update_other_users_insight(
    user_book_data,
    access_token,
    other_access_token,
    db_session,
):
    owner_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert owner_user_book_response.status_code == 201
    target_book_id = owner_user_book_response.json()["book_id"]

    other_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {other_access_token}"},
    )
    assert other_user_book_response.status_code == 201

    insight_response = client.post(
        f"/users/me/books/{target_book_id}/insights",
        json={"content": "所有者だけが変更できる気づき"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert insight_response.status_code == 201
    insight_id = insight_response.json()["id"]

    response = client.patch(
        f"/users/me/books/{target_book_id}/insights/{insight_id}",
        json={"content": "他人による変更"},
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert response.status_code == 404
    insight = db_session.get(Insight, insight_id)
    assert insight is not None
    assert insight.content == "所有者だけが変更できる気づき"


def test_update_insight_unauthorized_without_token(book_in_db):
    response = client.patch(
        f"/users/me/books/{book_in_db.id}/insights/1",
        json={"content": "変更後の気づき"},
    )

    assert response.status_code == 401
