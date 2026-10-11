import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from main import app
from models import BookRating

client = TestClient(app)


def test_update_book_rating_after_user_book_deletion(
    user_book_data, db_session, access_token, book_in_db
):
    user_book_response = client.post(
        "/users/me/books",
        json=user_book_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_book_response.status_code == 201
    book_id = user_book_response.json()["book_id"]

    update_user_book_status_response = client.patch(
        f"/users/me/books/{book_id}/status",
        json={"status": "completed", "recommendation_score": 5},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert update_user_book_status_response.status_code == 200

    delete_response = client.delete(
        f"/users/me/books/{book_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert delete_response.status_code == 204

    response = client.patch(
        f"/users/me/books/{book_id}/book-rating",
        json={"recommendation_score": 4},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["book_id"] == book_id
    assert response_data["title"] == book_in_db.title
    assert response_data["recommendation_score"] == 4
    book_rating_id = response_data["id"]

    book_rating = db_session.get(BookRating, book_rating_id)
    assert book_rating is not None
    assert book_rating.recommendation_score == response_data["recommendation_score"]


def test_update_book_rating_returns_not_found_when_rating_is_missing(
    book_in_db, registered_user, access_token, db_session
):
    response = client.patch(
        f"/users/me/books/{book_in_db.id}/book-rating",
        json={"recommendation_score": 4},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404

    statement = select(BookRating).where(
        BookRating.user_id == registered_user.id,
        BookRating.book_id == book_in_db.id,
    )
    book_rating = db_session.scalar(statement)
    assert book_rating is None


def test_update_book_rating_unauthorized_without_token(book_in_db):
    response = client.patch(
        f"/users/me/books/{book_in_db.id}/book-rating",
        json={"recommendation_score": 4},
    )

    assert response.status_code == 401


@pytest.mark.parametrize("book_id", ["abc", 0, -1])
def test_update_book_rating_rejects_invalid_book_id(book_id, access_token):
    response = client.patch(
        f"/users/me/books/{book_id}/book-rating",
        json={"recommendation_score": 4},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422


def test_update_book_rating_cannot_change_other_users_rating(
    book_in_db, other_user, access_token, db_session
):
    book_rating = BookRating(
        user_id=other_user.id,
        book_id=book_in_db.id,
        recommendation_score=5,
    )
    db_session.add(book_rating)
    db_session.commit()
    db_session.refresh(book_rating)

    try:
        response = client.patch(
            f"/users/me/books/{book_in_db.id}/book-rating",
            json={"recommendation_score": 4},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

        db_session.refresh(book_rating)
        assert book_rating.recommendation_score == 5
    finally:
        db_session.delete(book_rating)
        db_session.commit()


@pytest.mark.parametrize("recommendation_score", [0, 6])
def test_update_book_rating_rejects_out_of_range_score(
    recommendation_score, book_in_db, registered_user, access_token, db_session
):
    book_rating = BookRating(
        user_id=registered_user.id,
        book_id=book_in_db.id,
        recommendation_score=5,
    )
    db_session.add(book_rating)
    db_session.commit()
    db_session.refresh(book_rating)

    try:
        response = client.patch(
            f"/users/me/books/{book_in_db.id}/book-rating",
            json={"recommendation_score": recommendation_score},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

        db_session.refresh(book_rating)
        assert book_rating.recommendation_score == 5
    finally:
        db_session.delete(book_rating)
        db_session.commit()
