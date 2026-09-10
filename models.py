from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from enums import ReadingPriority


class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
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
    priority: Mapped[ReadingPriority] = mapped_column(
        Enum(ReadingPriority, name="reading_priority"), nullable=False
    )
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "book_id",
            name="uq_user_books_user_id_book_id",
        ),
    )
