from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    false,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from enums import BookGenre, ReadingPriority, ReadingStatus


class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    genre: Mapped[BookGenre] = mapped_column(
        Enum(BookGenre, name="book_genre"),
        nullable=False,
        default=BookGenre.OTHER,
    )
    isbn: Mapped[str | None] = mapped_column(
        String(13),
        unique=True,
        nullable=True,
    )


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=false())


class UserBook(Base):
    __tablename__ = "user_books"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    book: Mapped[Book] = relationship()
    insights: Mapped[list["Insight"]] = relationship(
        back_populates="user_book", cascade="all, delete-orphan", passive_deletes=True
    )
    priority: Mapped[ReadingPriority] = mapped_column(
        Enum(ReadingPriority, name="reading_priority"), nullable=False
    )
    status: Mapped[ReadingStatus] = mapped_column(
        Enum(ReadingStatus, name="reading_status"),
        nullable=False,
        default=ReadingStatus.WANT_TO_READ,
    )
    recommendation_score: Mapped[int | None] = mapped_column(nullable=True)
    reading_post: Mapped["ReadingPost | None"] = relationship(
        back_populates="user_book"
    )
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "book_id",
            name="uq_user_books_user_id_book_id",
        ),
        CheckConstraint(
            "recommendation_score IS NULL OR recommendation_score BETWEEN 1 AND 5",
            name="ck_user_books_recommendation_score_range",
        ),
        CheckConstraint(
            "status != 'COMPLETED' OR recommendation_score IS NOT NULL",
            name="ck_user_books_completed_requires_recommendation_score",
        ),
    )


class Insight(Base):
    __tablename__ = "insights"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_book_id: Mapped[int] = mapped_column(
        ForeignKey("user_books.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_book: Mapped[UserBook] = relationship(back_populates="insights")


class ReadingPost(Base):
    __tablename__ = "reading_posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    user_book_id: Mapped[int] = mapped_column(
        ForeignKey("user_books.id"), nullable=False
    )
    recommendation_reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    is_public: Mapped[bool] = mapped_column(
        default=True, server_default=true(), nullable=False
    )
    user_book: Mapped[UserBook] = relationship(back_populates="reading_post")
    __table_args__ = (
        UniqueConstraint("user_book_id", name="uq_reading_posts_user_book_id"),
        CheckConstraint(
            "char_length(recommendation_reason) BETWEEN 1 AND 1000",
            name="ck_reading_posts_recommendation_reason_length",
        ),
        CheckConstraint(
            "recommendation_reason ~ '[^[:space:]]'",
            name="ck_reading_posts_recommendation_reason_not_blank",
        ),
    )


class Like(Base):
    __tablename__ = "likes"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    reading_post_id: Mapped[int] = mapped_column(
        ForeignKey("reading_posts.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "reading_post_id",
            name="uq_likes_user_id_reading_post_id",
        ),
    )
