from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import Book, BookRating
from schemas.books import RelatedBookResponse


def get_related_books(book_id: int, db: Session) -> list[RelatedBookResponse] | None:
    book_statement = select(Book).where(Book.id == book_id)
    target_book = db.scalar(book_statement)
    if target_book is None:
        return None

    average_recommendation_score = func.avg(BookRating.recommendation_score).label(
        "average_recommendation_score"
    )

    related_books_statement = (
        select(
            Book.id.label("book_id"),
            Book.title,
            Book.cover_image_url,
            average_recommendation_score,
        )
        .outerjoin(BookRating, BookRating.book_id == Book.id)
        .where(Book.genre == target_book.genre, Book.id != target_book.id)
        .group_by(Book.id)
        .order_by(average_recommendation_score.desc().nulls_last())
        .limit(4)
    )

    related_books_rows = db.execute(related_books_statement).mappings().all()
    responses = []
    for row in related_books_rows:
        average_score = row["average_recommendation_score"]
        if average_score is not None:
            rounded_average_score = float(round(average_score, 1))
        else:
            rounded_average_score = None
        response = RelatedBookResponse(
            book_id=row["book_id"],
            title=row["title"],
            cover_image_url=row["cover_image_url"],
            average_recommendation_score=rounded_average_score,
        )
        responses.append(response)

    return responses
