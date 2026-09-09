import pytest
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker

from database import database_url, get_db
from main import app
from models import Book, User
from security import create_access_token, hash_password

TEST_DATABASE_URL = database_url.set(database="book_api_test")

test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def book_in_db():
    db = TestingSessionLocal()
    book = Book(
        title="テスト用の本",
        author="テスト著者",
        isbn=None,
    )
    db.add(book)
    db.commit()
    db.refresh(book)

    yield book

    db.delete(book)
    db.commit()
    db.close()


@pytest.fixture
def user_data():
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
    }

    yield data

    with TestingSessionLocal() as db:
        db.execute(delete(User).where(User.email == data["email"]))
        db.commit()


@pytest.fixture
def db_session():
    with TestingSessionLocal() as db:
        yield db


@pytest.fixture
def registered_user(user_data, db_session):
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=hash_password(user_data["password"]),
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def access_token(registered_user):
    return create_access_token(registered_user.id)


@pytest.fixture
def admin_user(registered_user, db_session):
    registered_user.is_admin = True
    db_session.commit()
    db_session.refresh(registered_user)

    return registered_user


@pytest.fixture
def admin_access_token(admin_user):
    return create_access_token(admin_user.id)


@pytest.fixture
def book_data():
    book = {
        "title": "テストA",
        "author": "著者A",
        "isbn": "1234567891234",
    }
    yield book

    with TestingSessionLocal() as db:
        db.execute(delete(Book).where(Book.isbn == book["isbn"]))
        db.commit()
