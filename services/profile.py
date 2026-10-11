from sqlalchemy import func, select
from sqlalchemy.orm import Session

from enums import ReadingStatus
from models import Book, Follow, ReadingPost, User, UserBook
from schemas.profiles import PublicBookshelfBookResponse, UserProfileResponse


def get_user_profile(user_id: int, db: Session) -> UserProfileResponse | None:
    user_statement = select(User).where(User.id == user_id)
    user = db.scalar(user_statement)

    if user is None:
        return None

    completed_book_count_statement = select(func.count(UserBook.id)).where(
        UserBook.user_id == user.id, UserBook.status == ReadingStatus.COMPLETED
    )
    completed_book_count = db.scalar(completed_book_count_statement)

    follower_count_statement = select(func.count(Follow.id)).where(
        Follow.followed_id == user.id
    )
    follower_count = db.scalar(follower_count_statement)

    public_books_statement = (
        select(
            ReadingPost.book_id,
            ReadingPost.id.label("reading_post_id"),
            Book.title,
            Book.author,
            Book.genre,
            Book.cover_image_url,
            ReadingPost.recommendation_score,
            ReadingPost.recommendation_reason,
        )
        .select_from(ReadingPost)
        .join(Book, ReadingPost.book_id == Book.id)
        .where(ReadingPost.user_id == user.id, ReadingPost.is_public.is_(True))
        .order_by(ReadingPost.created_at.desc())
    )
    public_book_rows = db.execute(public_books_statement).mappings().all()

    public_books = [PublicBookshelfBookResponse(**row) for row in public_book_rows]

    return UserProfileResponse(
        id=user.id,
        username=user.username,
        bio=user.bio,
        completed_book_count=completed_book_count,
        follower_count=follower_count,
        public_books=public_books,
    )
