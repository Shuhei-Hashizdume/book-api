from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from openai import APIError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from main import app
from models import AISuggestion, Book, Insight, UserBook
from schemas.ai_suggestion import AISuggestionOutput
from services import ai_suggestion as ai_suggestion_service

client = TestClient(app)


def test_set_ai_suggestion(user_book_data, access_token, db_session, monkeypatch):
    create_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_user_book_response.status_code == 201
    book_id = create_user_book_response.json()["book_id"]

    create_insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_insight_response.status_code == 201
    insight_id = create_insight_response.json()["id"]

    def fake_generate_ai_suggestion(content, title, author):
        ai_suggestion_response = AISuggestionOutput(
            clarified_insight="テストA",
            deep_dive="テストB",
            practical_application="テストC",
            next_action="テストD",
        )
        return ai_suggestion_response

    monkeypatch.setattr(
        ai_suggestion_service,
        "generate_ai_suggestion",
        fake_generate_ai_suggestion,
    )

    response = client.post(
        f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 201
    response_data = response.json()

    assert response_data["insight_id"] == insight_id
    assert response_data["clarified_insight"] == "テストA"
    assert response_data["deep_dive"] == "テストB"
    assert response_data["practical_application"] == "テストC"
    assert response_data["next_action"] == "テストD"

    ai_suggestion = db_session.get(AISuggestion, response_data["id"])
    assert ai_suggestion is not None
    assert ai_suggestion.insight_id == insight_id
    assert ai_suggestion.clarified_insight == "テストA"
    assert ai_suggestion.deep_dive == "テストB"
    assert ai_suggestion.practical_application == "テストC"
    assert ai_suggestion.next_action == "テストD"


def test_set_ai_suggestion_after_deleting_user_book(
    user_book_data, access_token, book_in_db, db_session, monkeypatch
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert user_book_response.status_code == 201
    user_book_id = user_book_response.json()["id"]
    book_id = user_book_response.json()["book_id"]

    insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
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

    def fake_generate_ai_suggestion(content, title, author):
        assert content == "小さな挑戦が大事"
        assert title == book_in_db.title
        assert author == book_in_db.author
        return AISuggestionOutput(
            clarified_insight="テストA",
            deep_dive="テストB",
            practical_application="テストC",
            next_action="テストD",
        )

    monkeypatch.setattr(
        ai_suggestion_service,
        "generate_ai_suggestion",
        fake_generate_ai_suggestion,
    )

    response = client.post(
        f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["insight_id"] == insight_id
    assert response_data["clarified_insight"] == "テストA"
    assert response_data["deep_dive"] == "テストB"
    assert response_data["practical_application"] == "テストC"
    assert response_data["next_action"] == "テストD"

    ai_suggestion = db_session.get(AISuggestion, response_data["id"])
    assert ai_suggestion is not None
    assert ai_suggestion.insight_id == insight_id
    assert ai_suggestion.clarified_insight == "テストA"
    assert ai_suggestion.deep_dive == "テストB"
    assert ai_suggestion.practical_application == "テストC"
    assert ai_suggestion.next_action == "テストD"


def test_regenerate_ai_suggestion(
    user_book_data, access_token, db_session, monkeypatch
):
    create_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_user_book_response.status_code == 201
    book_id = create_user_book_response.json()["book_id"]

    create_insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_insight_response.status_code == 201
    insight_id = create_insight_response.json()["id"]

    def fake_first_generation(content, title, author):
        return AISuggestionOutput(
            clarified_insight="初回A",
            deep_dive="初回B",
            practical_application="初回C",
            next_action="初回D",
        )

    monkeypatch.setattr(
        ai_suggestion_service, "generate_ai_suggestion", fake_first_generation
    )
    url = f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion"
    first_response = client.post(
        url, headers={"Authorization": f"Bearer {access_token}"}
    )
    assert first_response.status_code == 201
    suggestion_id = first_response.json()["id"]

    ai_suggestion = db_session.get(AISuggestion, suggestion_id)
    assert ai_suggestion is not None
    assert ai_suggestion.clarified_insight == "初回A"

    def fake_second_generation(content, title, author):
        return AISuggestionOutput(
            clarified_insight="更新A",
            deep_dive="更新B",
            practical_application="更新C",
            next_action="更新D",
        )

    monkeypatch.setattr(
        ai_suggestion_service, "generate_ai_suggestion", fake_second_generation
    )
    second_response = client.post(
        url, headers={"Authorization": f"Bearer {access_token}"}
    )
    assert second_response.status_code == 200
    response_data = second_response.json()
    assert response_data["id"] == suggestion_id
    assert response_data["insight_id"] == insight_id
    assert response_data["clarified_insight"] == "更新A"
    assert response_data["deep_dive"] == "更新B"
    assert response_data["practical_application"] == "更新C"
    assert response_data["next_action"] == "更新D"

    db_session.refresh(ai_suggestion)
    assert ai_suggestion.insight_id == insight_id
    assert ai_suggestion.clarified_insight == "更新A"
    assert ai_suggestion.deep_dive == "更新B"
    assert ai_suggestion.practical_application == "更新C"
    assert ai_suggestion.next_action == "更新D"

    suggestion_ids = db_session.scalars(
        select(AISuggestion.id).where(AISuggestion.insight_id == insight_id)
    ).all()
    assert suggestion_ids == [suggestion_id]


def test_set_ai_suggestion_return_without_access_token_error():
    response = client.post("/users/me/books/1/insights/1/ai_suggestion")
    assert response.status_code == 401


def test_set_ai_suggestion_return_without_insight_error(
    user_book_data, access_token, db_session
):
    create_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_user_book_response.status_code == 201
    book_id = create_user_book_response.json()["book_id"]

    response = client.post(
        f"/users/me/books/{book_id}/insights/1/ai_suggestion",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404


def test_set_ai_suggestion_return_other_access_token_error(
    user_book_data,
    access_token,
    other_access_token,
):
    create_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_user_book_response.status_code == 201
    book_id = create_user_book_response.json()["book_id"]

    create_insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_insight_response.status_code == 201
    insight_id = create_insight_response.json()["id"]

    response = client.post(
        f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert response.status_code == 404


def test_set_ai_suggestion_return_AISuggestionGenerationError(
    user_book_data, access_token, monkeypatch, db_session
):
    create_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_user_book_response.status_code == 201
    book_id = create_user_book_response.json()["book_id"]

    create_insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_insight_response.status_code == 201
    insight_id = create_insight_response.json()["id"]

    def fake_generate_ai_suggestion(content, title, author):
        raise ai_suggestion_service.AISuggestionGenerationError

    monkeypatch.setattr(
        ai_suggestion_service,
        "generate_ai_suggestion",
        fake_generate_ai_suggestion,
    )

    response = client.post(
        f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 500

    statement = select(AISuggestion).where(AISuggestion.insight_id == insight_id)
    ai_suggestion = db_session.scalar(statement)
    assert ai_suggestion is None


def test_set_ai_suggestion_return_AISuggestionSaveError(
    user_book_data, access_token, db_session, monkeypatch
):
    create_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_user_book_response.status_code == 201
    book_id = create_user_book_response.json()["book_id"]

    create_insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_insight_response.status_code == 201
    insight_id = create_insight_response.json()["id"]

    def fake_generate_ai_suggestion(content, title, author):
        raise ai_suggestion_service.AISuggestionSaveError

    monkeypatch.setattr(
        ai_suggestion_service,
        "generate_ai_suggestion",
        fake_generate_ai_suggestion,
    )

    response = client.post(
        f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 500

    statement = select(AISuggestion).where(AISuggestion.insight_id == insight_id)
    ai_suggestion = db_session.scalar(statement)
    assert ai_suggestion is None


def test_set_ai_suggestion_return_IntegrityError(
    user_book_data, access_token, db_session, monkeypatch
):
    create_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_user_book_response.status_code == 201
    book_id = create_user_book_response.json()["book_id"]

    create_insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_insight_response.status_code == 201
    insight_id = create_insight_response.json()["id"]

    def fake_generate_ai_suggestion(content, title, author):
        ai_suggestion_response = AISuggestionOutput(
            clarified_insight="テストA",
            deep_dive="テストB",
            practical_application="テストC",
            next_action="テストD",
        )
        return ai_suggestion_response

    def fake_commit(_session):
        raise IntegrityError(
            "INSERT INTO ai_suggestions", {}, Exception("テスト用の保存失敗")
        )

    monkeypatch.setattr(
        ai_suggestion_service,
        "generate_ai_suggestion",
        fake_generate_ai_suggestion,
    )

    rollback_was_called = False
    original_rollback = Session.rollback

    def record_rollback(session):
        nonlocal rollback_was_called
        rollback_was_called = True
        return original_rollback(session)

    with monkeypatch.context() as patch:
        patch.setattr(Session, "commit", fake_commit)
        patch.setattr(Session, "rollback", record_rollback)
        response = client.post(
            f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert response.status_code == 500
    assert rollback_was_called is True

    statement = select(AISuggestion).where(AISuggestion.insight_id == insight_id)
    ai_suggestion = db_session.scalar(statement)
    assert ai_suggestion is None


@pytest.mark.parametrize(
    "book_id,insight_id",
    [
        (0, 1),
        (-1, 1),
        (1, 0),
        (1, -1),
    ],
)
def test_set_ai_suggestion_returns_422_for_invalid_path_ids(
    book_id, insight_id, access_token
):
    response = client.post(
        f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422


def test_generate_ai_suggestion_raises_on_api_error(monkeypatch):
    fake_client = Mock()
    fake_client.responses.parse.side_effect = APIError(
        "テスト用のAPI失敗",
        request=Mock(),
        body=None,
    )

    def fake_openai(api_key):
        return fake_client

    monkeypatch.setattr(ai_suggestion_service, "OpenAI", fake_openai)

    with pytest.raises(ai_suggestion_service.AISuggestionGenerationError):
        ai_suggestion_service.generate_ai_suggestion(
            content="小さな挑戦が大事",
            title="テスト用の本",
            author="テスト著者",
        )


def test_generate_ai_suggestion_raises_when_output_parsed_is_none(monkeypatch):
    fake_client = Mock()
    fake_client.responses.parse.return_value.output_parsed = None

    def fake_openai(api_key):
        return fake_client

    monkeypatch.setattr(ai_suggestion_service, "OpenAI", fake_openai)

    with pytest.raises(ai_suggestion_service.AISuggestionGenerationError):
        ai_suggestion_service.generate_ai_suggestion(
            content="小さな挑戦が大事",
            title="テスト用の本",
            author="テスト著者",
        )


def test_generate_ai_suggestion_returns_parsed_output(monkeypatch):
    expected_suggestion = AISuggestionOutput(
        clarified_insight="テストA",
        deep_dive="テストB",
        practical_application="テストC",
        next_action="テストD",
    )

    fake_client = Mock()
    fake_client.responses.parse.return_value.output_parsed = expected_suggestion

    def fake_openai(api_key):
        return fake_client

    monkeypatch.setattr(ai_suggestion_service, "OpenAI", fake_openai)

    suggestion = ai_suggestion_service.generate_ai_suggestion(
        content="小さな挑戦が大事",
        title="テスト用の本",
        author="テスト著者",
    )

    assert suggestion == expected_suggestion


def test_read_users_ai_suggestion(user_book_data, access_token, db_session):
    create_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_user_book_response.status_code == 201
    book_id = create_user_book_response.json()["book_id"]

    create_insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_insight_response.status_code == 201
    insight_id = create_insight_response.json()["id"]

    ai_suggestion = AISuggestion(
        insight_id=insight_id,
        clarified_insight="テストA",
        deep_dive="テストB",
        practical_application="テストC",
        next_action="テストD",
    )

    db_session.add(ai_suggestion)
    db_session.commit()
    db_session.refresh(ai_suggestion)

    response = client.get(
        f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    response_data = response.json()

    assert response_data["id"] == ai_suggestion.id
    assert response_data["insight_id"] == insight_id
    assert response_data["clarified_insight"] == "テストA"
    assert response_data["deep_dive"] == "テストB"
    assert response_data["practical_application"] == "テストC"
    assert response_data["next_action"] == "テストD"


def test_read_ai_suggestion_after_deleting_user_book(
    user_book_data, access_token, db_session
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert user_book_response.status_code == 201
    user_book_id = user_book_response.json()["id"]
    book_id = user_book_response.json()["book_id"]

    insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert insight_response.status_code == 201
    insight_id = insight_response.json()["id"]

    ai_suggestion = AISuggestion(
        insight_id=insight_id,
        clarified_insight="テストA",
        deep_dive="テストB",
        practical_application="テストC",
        next_action="テストD",
    )
    db_session.add(ai_suggestion)
    db_session.commit()
    db_session.refresh(ai_suggestion)
    ai_suggestion_id = ai_suggestion.id

    delete_response = client.delete(
        f"/users/me/books/{book_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert delete_response.status_code == 204
    assert db_session.get(UserBook, user_book_id) is None

    response = client.get(
        f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == ai_suggestion_id
    assert response_data["insight_id"] == insight_id
    assert response_data["clarified_insight"] == "テストA"
    assert response_data["deep_dive"] == "テストB"
    assert response_data["practical_application"] == "テストC"
    assert response_data["next_action"] == "テストD"


def test_read_users_ai_suggestion_returns_404_when_not_registered(
    user_book_data, access_token
):
    create_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_user_book_response.status_code == 201
    book_id = create_user_book_response.json()["book_id"]

    create_insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_insight_response.status_code == 201
    insight_id = create_insight_response.json()["id"]

    response = client.get(
        f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "AI提案が保存されていません。"}


def test_read_users_ai_suggestion_returns_401_without_access_token():
    response = client.get("/users/me/books/1/insights/1/ai_suggestion")

    assert response.status_code == 401


@pytest.mark.parametrize(
    "book_id,insight_id",
    [
        (0, 1),
        (-1, 1),
        (1, 0),
        (1, -1),
    ],
)
def test_read_users_ai_suggestion_returns_422_for_invalid_path_ids(
    book_id, insight_id, access_token
):
    response = client.get(
        f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422


def test_read_users_ai_suggestion_returns_404_for_other_user(
    user_book_data, access_token, other_access_token, db_session
):
    create_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_user_book_response.status_code == 201
    book_id = create_user_book_response.json()["book_id"]

    create_insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_insight_response.status_code == 201
    insight_id = create_insight_response.json()["id"]

    ai_suggestion = AISuggestion(
        insight_id=insight_id,
        clarified_insight="テストA",
        deep_dive="テストB",
        practical_application="テストC",
        next_action="テストD",
    )
    db_session.add(ai_suggestion)
    db_session.commit()

    response = client.get(
        f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "AI提案が保存されていません。"}


def test_read_users_ai_suggestion_returns_404_for_different_book(
    user_book_data, book_data, access_token, db_session
):
    create_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_user_book_response.status_code == 201
    book_id = create_user_book_response.json()["book_id"]

    create_insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_insight_response.status_code == 201
    insight_id = create_insight_response.json()["id"]

    ai_suggestion = AISuggestion(
        insight_id=insight_id,
        clarified_insight="テストA",
        deep_dive="テストB",
        practical_application="テストC",
        next_action="テストD",
    )
    different_book = Book(**book_data)
    db_session.add_all([ai_suggestion, different_book])
    db_session.commit()
    db_session.refresh(different_book)
    assert different_book.id != book_id

    create_different_user_book_response = client.post(
        "/users/me/books",
        json={"book_id": different_book.id, "priority": "high"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_different_user_book_response.status_code == 201

    different_user_book = db_session.scalar(
        select(UserBook).where(
            UserBook.id == create_different_user_book_response.json()["id"]
        )
    )
    try:
        response = client.get(
            f"/users/me/books/{different_book.id}/insights/{insight_id}/ai_suggestion",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "AI提案が保存されていません。"}
    finally:
        db_session.delete(different_user_book)
        db_session.commit()


def test_delete_ai_suggestion(user_book_data, access_token, db_session):
    create_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_user_book_response.status_code == 201
    book_id = create_user_book_response.json()["book_id"]

    create_insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert create_insight_response.status_code == 201
    insight_id = create_insight_response.json()["id"]

    ai_suggestion = AISuggestion(
        insight_id=insight_id,
        clarified_insight="テストA",
        deep_dive="テストB",
        practical_application="テストC",
        next_action="テストD",
    )

    db_session.add(ai_suggestion)
    db_session.commit()
    db_session.refresh(ai_suggestion)

    ai_suggestion_id = ai_suggestion.id

    response = client.delete(
        f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 204
    assert response.text == ""

    statement = select(AISuggestion).where(AISuggestion.id == ai_suggestion_id)
    assert db_session.scalar(statement) is None


def test_delete_ai_suggestion_after_deleting_user_book(
    user_book_data, access_token, db_session
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert user_book_response.status_code == 201
    user_book_id = user_book_response.json()["id"]
    book_id = user_book_response.json()["book_id"]

    insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert insight_response.status_code == 201
    insight_id = insight_response.json()["id"]

    ai_suggestion = AISuggestion(
        insight_id=insight_id,
        clarified_insight="テストA",
        deep_dive="テストB",
        practical_application="テストC",
        next_action="テストD",
    )
    db_session.add(ai_suggestion)
    db_session.commit()
    db_session.refresh(ai_suggestion)
    ai_suggestion_id = ai_suggestion.id

    user_book_delete_response = client.delete(
        f"/users/me/books/{book_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert user_book_delete_response.status_code == 204
    assert db_session.get(UserBook, user_book_id) is None

    response = client.delete(
        f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 204
    assert response.text == ""

    statement = select(AISuggestion).where(AISuggestion.id == ai_suggestion_id)
    assert db_session.scalar(statement) is None

    insight = db_session.get(Insight, insight_id)
    assert insight is not None
    assert insight.content == "小さな挑戦が大事"
    assert insight.book_id == book_id


def test_delete_insight_deletes_ai_suggestion_after_deleting_user_book(
    user_book_data, access_token, db_session
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert user_book_response.status_code == 201
    user_book_id = user_book_response.json()["id"]
    book_id = user_book_response.json()["book_id"]

    insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert insight_response.status_code == 201
    insight_id = insight_response.json()["id"]

    ai_suggestion = AISuggestion(
        insight_id=insight_id,
        clarified_insight="テストA",
        deep_dive="テストB",
        practical_application="テストC",
        next_action="テストD",
    )
    db_session.add(ai_suggestion)
    db_session.commit()
    db_session.refresh(ai_suggestion)
    ai_suggestion_id = ai_suggestion.id

    user_book_delete_response = client.delete(
        f"/users/me/books/{book_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert user_book_delete_response.status_code == 204
    assert db_session.get(UserBook, user_book_id) is None
    assert db_session.scalar(select(Insight).where(Insight.id == insight_id)) is not None
    assert db_session.scalar(
        select(AISuggestion).where(AISuggestion.id == ai_suggestion_id)
    ) is not None

    response = client.delete(
        f"/users/me/books/{book_id}/insights/{insight_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 204
    assert response.text == ""
    assert db_session.scalar(select(Insight).where(Insight.id == insight_id)) is None
    assert db_session.scalar(
        select(AISuggestion).where(AISuggestion.id == ai_suggestion_id)
    ) is None


def test_delete_ai_suggestion_returns_404_when_not_registered(
    user_book_data, access_token
):
    create_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_user_book_response.status_code == 201
    book_id = create_user_book_response.json()["book_id"]

    create_insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_insight_response.status_code == 201
    insight_id = create_insight_response.json()["id"]

    response = client.delete(
        f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "AI提案が保存されていません。"}


def test_delete_ai_suggestion_returns_401_without_access_token():
    response = client.delete("/users/me/books/1/insights/1/ai_suggestion")

    assert response.status_code == 401


@pytest.mark.parametrize(
    "book_id,insight_id",
    [
        (0, 1),
        (-1, 1),
        (1, 0),
        (1, -1),
    ],
)
def test_delete_ai_suggestion_returns_422_for_invalid_path_ids(
    book_id, insight_id, access_token
):
    response = client.delete(
        f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422


def test_delete_ai_suggestion_returns_404_for_other_user(
    user_book_data, access_token, other_access_token, db_session
):
    create_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_user_book_response.status_code == 201
    book_id = create_user_book_response.json()["book_id"]

    create_insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_insight_response.status_code == 201
    insight_id = create_insight_response.json()["id"]

    ai_suggestion = AISuggestion(
        insight_id=insight_id,
        clarified_insight="テストA",
        deep_dive="テストB",
        practical_application="テストC",
        next_action="テストD",
    )
    db_session.add(ai_suggestion)
    db_session.commit()
    db_session.refresh(ai_suggestion)
    ai_suggestion_id = ai_suggestion.id

    response = client.delete(
        f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion",
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "AI提案が保存されていません。"}

    statement = select(AISuggestion).where(AISuggestion.id == ai_suggestion_id)
    assert db_session.scalar(statement) is not None


def test_delete_ai_suggestion_returns_404_for_different_book(
    user_book_data, book_data, access_token, db_session
):
    create_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_user_book_response.status_code == 201
    book_id = create_user_book_response.json()["book_id"]

    create_insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_insight_response.status_code == 201
    insight_id = create_insight_response.json()["id"]

    ai_suggestion = AISuggestion(
        insight_id=insight_id,
        clarified_insight="テストA",
        deep_dive="テストB",
        practical_application="テストC",
        next_action="テストD",
    )
    different_book = Book(**book_data)
    db_session.add_all([ai_suggestion, different_book])
    db_session.commit()
    db_session.refresh(ai_suggestion)
    db_session.refresh(different_book)
    ai_suggestion_id = ai_suggestion.id
    assert different_book.id != book_id

    create_different_user_book_response = client.post(
        "/users/me/books",
        json={"book_id": different_book.id, "priority": "high"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_different_user_book_response.status_code == 201

    different_user_book = db_session.scalar(
        select(UserBook).where(
            UserBook.id == create_different_user_book_response.json()["id"]
        )
    )
    try:
        response = client.delete(
            f"/users/me/books/{different_book.id}/insights/{insight_id}/ai_suggestion",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "AI提案が保存されていません。"}

        statement = select(AISuggestion).where(AISuggestion.id == ai_suggestion_id)
        assert db_session.scalar(statement) is not None
    finally:
        db_session.delete(different_user_book)
        db_session.commit()


def test_regenerate_ai_suggestion_preserves_existing_suggestion_on_generation_error(
    user_book_data, access_token, db_session, monkeypatch
):
    create_user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_user_book_response.status_code == 201
    book_id = create_user_book_response.json()["book_id"]

    create_insight_response = client.post(
        f"/users/me/books/{book_id}/insights",
        json={"content": "小さな挑戦が大事"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_insight_response.status_code == 201
    insight_id = create_insight_response.json()["id"]

    ai_suggestion = AISuggestion(
        insight_id=insight_id,
        clarified_insight="保存済みA",
        deep_dive="保存済みB",
        practical_application="保存済みC",
        next_action="保存済みD",
    )
    db_session.add(ai_suggestion)
    db_session.commit()
    db_session.refresh(ai_suggestion)
    ai_suggestion_id = ai_suggestion.id

    def fake_generate_ai_suggestion(content, title, author):
        raise ai_suggestion_service.AISuggestionGenerationError

    monkeypatch.setattr(
        ai_suggestion_service,
        "generate_ai_suggestion",
        fake_generate_ai_suggestion,
    )

    response = client.post(
        f"/users/me/books/{book_id}/insights/{insight_id}/ai_suggestion",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 500

    db_session.refresh(ai_suggestion)
    assert ai_suggestion.id == ai_suggestion_id
    assert ai_suggestion.insight_id == insight_id
    assert ai_suggestion.clarified_insight == "保存済みA"
    assert ai_suggestion.deep_dive == "保存済みB"
    assert ai_suggestion.practical_application == "保存済みC"
    assert ai_suggestion.next_action == "保存済みD"
    assert db_session.scalars(
        select(AISuggestion.id).where(AISuggestion.insight_id == insight_id)
    ).all() == [ai_suggestion_id]
