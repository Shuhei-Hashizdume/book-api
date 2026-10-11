from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Book, Follow, ReadingPost, User
from schemas.timelines import TimelinePostResponse


def _build_base_timeline_statement():
    base_timeline_statement = (
        select(
            User.id.label("user_id"),
            User.username,
            Book.id.label("book_id"),
            Book.title,
            Book.cover_image_url,
            ReadingPost.recommendation_score,
            ReadingPost.recommendation_reason,
            ReadingPost.created_at,
            ReadingPost.id.label("reading_post_id"),
        )
        .select_from(ReadingPost)
        .join(Book, ReadingPost.book_id == Book.id)
        .join(User, ReadingPost.user_id == User.id)
    )
    return base_timeline_statement


def get_recommended_timeline(db: Session) -> list[TimelinePostResponse]:

    base_statement = _build_base_timeline_statement()
    recommended_statement = base_statement.where(
        ReadingPost.is_public.is_(True)
    ).order_by(ReadingPost.created_at.desc())

    recommended_timeline_rows = db.execute(recommended_statement).mappings().all()
    recommended_timeline = [
        TimelinePostResponse(**row) for row in recommended_timeline_rows
    ]
    return recommended_timeline


def get_following_timeline(
    current_user_id: int, db: Session
) -> list[TimelinePostResponse]:
    base_statement = _build_base_timeline_statement()
    following_timeline_statement = (
        base_statement.join(Follow, User.id == Follow.followed_id)
        .where(
            Follow.follower_id == current_user_id,
            ReadingPost.is_public.is_(True),
        )
        .order_by(ReadingPost.created_at.desc())
    )
    following_timeline_rows = db.execute(following_timeline_statement).mappings().all()
    following_timeline = [
        TimelinePostResponse(**row) for row in following_timeline_rows
    ]
    return following_timeline
