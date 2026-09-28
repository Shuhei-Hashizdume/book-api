import pytest
from fastapi.testclient import TestClient

from enums import BookGenre, ReadingPriority, ReadingStatus
from main import app
from models import Book, UserBook

client = TestClient(app)


def test_read_related_books_returns_book_in_same_genre(
    book_in_db, registered_user, other_user, third_user, db_session
):
    same_genre_book = Book(
        title="テストA",
        author="著者A",
        genre=book_in_db.genre,
        cover_image_url="https://example.com/related-book-cover.jpg",
    )

    different_genre_book = Book(
        title="テストB",
        author="著者B",
        genre=BookGenre.BUSINESS,
    )

    db_session.add_all([same_genre_book, different_genre_book])
    db_session.commit()
    db_session.refresh(same_genre_book)
    db_session.refresh(different_genre_book)

    same_genre_user_book = UserBook(
        user_id=registered_user.id,
        book_id=same_genre_book.id,
        priority=ReadingPriority.MEDIUM,
        status=ReadingStatus.COMPLETED,
        recommendation_score=5,
    )
    other_user_same_genre_user_book = UserBook(
        user_id=other_user.id,
        book_id=same_genre_book.id,
        priority=ReadingPriority.MEDIUM,
        status=ReadingStatus.COMPLETED,
        recommendation_score=4,
    )
    third_user_same_genre_user_book = UserBook(
        user_id=third_user.id,
        book_id=same_genre_book.id,
        priority=ReadingPriority.MEDIUM,
        status=ReadingStatus.COMPLETED,
        recommendation_score=4,
    )

    different_genre_user_book = UserBook(
        user_id=registered_user.id,
        book_id=different_genre_book.id,
        priority=ReadingPriority.MEDIUM,
        status=ReadingStatus.COMPLETED,
        recommendation_score=4,
    )

    db_session.add_all(
        [
            same_genre_user_book,
            other_user_same_genre_user_book,
            third_user_same_genre_user_book,
            different_genre_user_book,
        ]
    )
    db_session.commit()
    db_session.refresh(same_genre_user_book)
    db_session.refresh(other_user_same_genre_user_book)
    db_session.refresh(third_user_same_genre_user_book)
    db_session.refresh(different_genre_user_book)

    try:
        response = client.get(f"/books/{book_in_db.id}/related")
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 1
        assert response_data[0]["title"] == same_genre_book.title
        assert response_data[0]["book_id"] == same_genre_book.id
        assert (
            response_data[0]["cover_image_url"]
            == "https://example.com/related-book-cover.jpg"
        )
        assert response_data[0]["average_recommendation_score"] == 4.3
    finally:
        db_session.delete(same_genre_user_book)
        db_session.delete(other_user_same_genre_user_book)
        db_session.delete(third_user_same_genre_user_book)
        db_session.delete(different_genre_user_book)
        db_session.flush()

        db_session.delete(same_genre_book)
        db_session.delete(different_genre_book)
        db_session.commit()


def test_read_related_books_returns_book_without_rating(book_in_db, db_session):
    same_genre_book = Book(
        title="テストA",
        author="著者A",
        genre=book_in_db.genre,
    )

    db_session.add(same_genre_book)
    db_session.commit()
    db_session.refresh(same_genre_book)

    try:
        response = client.get(f"/books/{book_in_db.id}/related")
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 1
        assert response_data[0]["average_recommendation_score"] is None
        assert response_data[0]["book_id"] == same_genre_book.id
        assert response_data[0]["title"] == same_genre_book.title
        assert response_data[0]["cover_image_url"] is None
    finally:
        db_session.delete(same_genre_book)
        db_session.commit()


def test_read_related_books_returns_empty_list_when_no_related_books(book_in_db):
    response = client.get(f"/books/{book_in_db.id}/related")
    assert response.status_code == 200
    assert response.json() == []


def test_read_related_books_returns_not_found_for_missing_book():
    response = client.get("/books/999999/related")
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "本が見つかりません。"


def test_read_related_books_returns_at_most_four_books(book_in_db, db_session):
    related_books = [
        Book(
            title=f"関連書籍{index}",
            author=f"著者{index}",
            genre=book_in_db.genre,
        )
        for index in range(5)
    ]
    db_session.add_all(related_books)
    db_session.commit()

    try:
        response = client.get(f"/books/{book_in_db.id}/related")

        assert response.status_code == 200
        assert len(response.json()) == 4
    finally:
        for book in related_books:
            db_session.delete(book)
        db_session.commit()


def test_read_related_books_orders_by_average_score_with_unrated_last(
    book_in_db, registered_user, db_session
):
    low_score_book = Book(
        title="低評価の関連書籍",
        author="著者A",
        genre=book_in_db.genre,
    )
    high_score_book = Book(
        title="高評価の関連書籍",
        author="著者B",
        genre=book_in_db.genre,
    )
    unrated_book = Book(
        title="未評価の関連書籍",
        author="著者C",
        genre=book_in_db.genre,
    )
    db_session.add_all([low_score_book, high_score_book, unrated_book])
    db_session.commit()
    db_session.refresh(low_score_book)
    db_session.refresh(high_score_book)
    db_session.refresh(unrated_book)

    low_score_user_book = UserBook(
        user_id=registered_user.id,
        book_id=low_score_book.id,
        priority=ReadingPriority.MEDIUM,
        status=ReadingStatus.COMPLETED,
        recommendation_score=2,
    )
    high_score_user_book = UserBook(
        user_id=registered_user.id,
        book_id=high_score_book.id,
        priority=ReadingPriority.MEDIUM,
        status=ReadingStatus.COMPLETED,
        recommendation_score=5,
    )
    db_session.add_all([low_score_user_book, high_score_user_book])
    db_session.commit()

    try:
        response = client.get(f"/books/{book_in_db.id}/related")

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 3
        returned_book_ids = [book["book_id"] for book in response_data]
        assert returned_book_ids == [
            high_score_book.id,
            low_score_book.id,
            unrated_book.id,
        ]
    finally:
        db_session.delete(low_score_user_book)
        db_session.delete(high_score_user_book)
        db_session.flush()

        db_session.delete(low_score_book)
        db_session.delete(high_score_book)
        db_session.delete(unrated_book)
        db_session.commit()


@pytest.mark.parametrize("book_id", [0, -1])
def test_read_related_books_rejects_non_positive_book_id(book_id):
    response = client.get(f"/books/{book_id}/related")
    assert response.status_code == 422
