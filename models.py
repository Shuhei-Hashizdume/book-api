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
from enums import BookGenre, ReadingPriority, ReadingReminderStatus, ReadingStatus


class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str | None] = mapped_column(nullable=True)
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
    cover_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    __table_args__ = (
        UniqueConstraint(
            "external_id",
            name="uq_books_external_id",
        ),
    )


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=false())
    bio: Mapped[str | None] = mapped_column(Text)
    following_relationships: Mapped[list["Follow"]] = relationship(
        back_populates="follower",
        foreign_keys="Follow.follower_id",
        cascade="all, delete",
        passive_deletes=True,
    )
    follower_relationships: Mapped[list["Follow"]] = relationship(
        back_populates="followed",
        foreign_keys="Follow.followed_id",
        cascade="all, delete",
        passive_deletes=True,
    )
    __table_args__ = (
        CheckConstraint(
            "bio IS NULL OR char_length(bio) BETWEEN 1 AND 160",
            name="ck_users_bio_range",
        ),
        CheckConstraint(
            "bio IS NULL OR bio ~ '[^[:space:]]'",
            name="ck_users_bio_not_blank",
        ),
    )


class UserBook(Base):
    __tablename__ = "user_books"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    book: Mapped[Book] = relationship()

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
    reading_reminder: Mapped["ReadingReminder | None"] = relationship(
        back_populates="user_book", cascade="all, delete-orphan", passive_deletes=True
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
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    book: Mapped[Book] = relationship()
    content: Mapped[str] = mapped_column(Text, nullable=False)
    ai_suggestion: Mapped["AISuggestion | None"] = relationship(
        cascade="all,delete-orphan", passive_deletes=True, back_populates="insight"
    )


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


class Follow(Base):
    __tablename__ = "follows"
    id: Mapped[int] = mapped_column(primary_key=True)
    follower_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    followed_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    follower: Mapped[User] = relationship(
        back_populates="following_relationships",
        foreign_keys=[follower_id],
    )
    followed: Mapped[User] = relationship(
        back_populates="follower_relationships", foreign_keys=[followed_id]
    )

    __table_args__ = (
        UniqueConstraint(
            "follower_id", "followed_id", name="uq_follows_follower_id_followed_id"
        ),
        CheckConstraint(
            "follower_id != followed_id", name="ck_follows_different_users"
        ),
    )


class ReadingReminder(Base):
    __tablename__ = "reading_reminders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_book_id: Mapped[int] = mapped_column(
        ForeignKey("user_books.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[ReadingReminderStatus] = mapped_column(
        Enum(ReadingReminderStatus, name="reading_reminder_status"),
        nullable=False,
        default=ReadingReminderStatus.ACTIVE,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    next_send_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    user_book: Mapped[UserBook] = relationship(back_populates="reading_reminder")
    __table_args__ = (
        UniqueConstraint("user_book_id", name="uq_reading_reminders_user_book_id"),
    )


class AISuggestion(Base):
    __tablename__ = "ai_suggestions"
    id: Mapped[int] = mapped_column(primary_key=True)
    insight_id: Mapped[int] = mapped_column(
        ForeignKey("insights.id", ondelete="CASCADE"), nullable=False
    )
    clarified_insight: Mapped[str] = mapped_column(Text, nullable=False)
    deep_dive: Mapped[str] = mapped_column(Text, nullable=False)
    practical_application: Mapped[str] = mapped_column(Text, nullable=False)
    next_action: Mapped[str] = mapped_column(Text, nullable=False)
    insight: Mapped[Insight] = relationship(back_populates="ai_suggestion")
    __table_args__ = (
        UniqueConstraint("insight_id", name="uq_ai_suggestion_insight_id"),
    )
