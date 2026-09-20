from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import Book, UserBook
from schemas.books import BookDetailResponse


def get_book_with_average_score(book_id: int, db: Session) -> BookDetailResponse | None:
    statement = (
        select(Book, func.avg(UserBook.recommendation_score))
        .outerjoin(UserBook, UserBook.book_id == Book.id)
        .where(Book.id == book_id)
        .group_by(Book.id)
    )
    result = db.execute(statement).one_or_none()

    if result is None:
        return None

    book, average_score = result

    rounded_average_score = (
        float(round(average_score, 1)) if average_score is not None else None
    )

    return BookDetailResponse(
        id=book.id,
        title=book.title,
        author=book.author,
        genre=book.genre,
        average_recommendation_score=rounded_average_score,
    )
