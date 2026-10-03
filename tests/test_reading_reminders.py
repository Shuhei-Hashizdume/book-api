from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from enums import ReadingReminderStatus, ReadingStatus
from main import app
from models import ReadingReminder, UserBook
from services import reading_reminders as reading_reminder_service
from services.email import EmailSendError
from services.reading_reminders import (
    get_due_reading_reminders,
    process_due_reading_reminder,
)

client = TestClient(app)


def test_set_user_book_reading_reminder(
    user_book_data, access_token, db_session, registered_user
):
    user_book = UserBook(
        book_id=user_book_data["book_id"],
        user_id=registered_user.id,
        priority=user_book_data["priority"],
        status=ReadingStatus.READING,
    )

    db_session.add(user_book)
    db_session.commit()
    db_session.refresh(user_book)

    response = client.post(
        f"/users/me/books/{user_book.book_id}/reminder",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["user_book_id"] == user_book.id
    assert response_data["status"] == "active"

    reading_reminder = db_session.get(ReadingReminder, response_data["id"])
    assert reading_reminder is not None
    assert reading_reminder.status == ReadingReminderStatus.ACTIVE
    assert reading_reminder.user_book_id == user_book.id
    assert reading_reminder.started_at is not None
    assert reading_reminder.next_send_at == datetime.fromisoformat(
        response_data["next_send_at"]
    )

    jst = ZoneInfo("Asia/Tokyo")

    started_at_jst = reading_reminder.started_at.astimezone(jst)
    next_send_at_jst = reading_reminder.next_send_at.astimezone(jst)
    assert next_send_at_jst.date() == started_at_jst.date() + timedelta(days=7)
    assert next_send_at_jst.hour == 20
    assert next_send_at_jst.minute == 0
    assert next_send_at_jst.second == 0


def test_reset_user_book_reading_reminder(
    user_book_data, access_token, db_session, registered_user
):
    user_book = UserBook(
        book_id=user_book_data["book_id"],
        user_id=registered_user.id,
        priority=user_book_data["priority"],
        status=ReadingStatus.READING,
    )

    db_session.add(user_book)
    db_session.commit()
    db_session.refresh(user_book)

    jst = ZoneInfo("Asia/Tokyo")
    reading_reminder = ReadingReminder(
        user_book_id=user_book.id,
        status=ReadingReminderStatus.SEND_ACCEPTED,
        started_at=datetime(
            2026,
            9,
            1,
            12,
            0,
            tzinfo=jst,
        ),
        next_send_at=datetime(
            2026,
            9,
            8,
            20,
            0,
            tzinfo=jst,
        ),
    )

    db_session.add(reading_reminder)
    db_session.commit()
    db_session.refresh(reading_reminder)

    response = client.post(
        f"/users/me/books/{user_book.book_id}/reminder",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "active"
    assert response_data["id"] == reading_reminder.id

    db_session.refresh(reading_reminder)
    assert reading_reminder is not None
    assert reading_reminder.status == ReadingReminderStatus.ACTIVE
    assert reading_reminder.user_book_id == user_book.id
    assert reading_reminder.started_at is not None
    assert reading_reminder.next_send_at == datetime.fromisoformat(
        response_data["next_send_at"]
    )

    jst = ZoneInfo("Asia/Tokyo")

    started_at_jst = reading_reminder.started_at.astimezone(jst)
    next_send_at_jst = reading_reminder.next_send_at.astimezone(jst)
    assert next_send_at_jst.date() == started_at_jst.date() + timedelta(days=7)
    assert next_send_at_jst.hour == 20
    assert next_send_at_jst.minute == 0
    assert next_send_at_jst.second == 0


def test_set_user_book_reading_reminder_returns_not_found_user_book(
    book_in_db, access_token
):
    response = client.post(
        f"/users/me/books/{book_in_db.id}/reminder",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404


def test_set_user_book_reading_reminder_returns_conflict_when_want_to_read(
    user_book_data, access_token, db_session, registered_user
):
    user_book = UserBook(
        book_id=user_book_data["book_id"],
        user_id=registered_user.id,
        priority=user_book_data["priority"],
        status=ReadingStatus.WANT_TO_READ,
    )

    db_session.add(user_book)
    db_session.commit()
    db_session.refresh(user_book)

    response = client.post(
        f"/users/me/books/{user_book.book_id}/reminder",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 409


def test_set_user_book_reading_reminder_returns_conflict_when_completed(
    user_book_data, access_token, db_session, registered_user
):
    user_book = UserBook(
        book_id=user_book_data["book_id"],
        user_id=registered_user.id,
        priority=user_book_data["priority"],
        status=ReadingStatus.COMPLETED,
        recommendation_score=5,
    )

    db_session.add(user_book)
    db_session.commit()
    db_session.refresh(user_book)

    response = client.post(
        f"/users/me/books/{user_book.book_id}/reminder",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 409


def test_set_user_book_reading_reminder_returns_conflict_when_already_active(
    user_book_data, access_token, db_session, registered_user
):
    user_book = UserBook(
        book_id=user_book_data["book_id"],
        user_id=registered_user.id,
        priority=user_book_data["priority"],
        status=ReadingStatus.READING,
    )
    db_session.add(user_book)
    db_session.commit()
    db_session.refresh(user_book)

    jst = ZoneInfo("Asia/Tokyo")
    reading_reminder = ReadingReminder(
        user_book_id=user_book.id,
        status=ReadingReminderStatus.ACTIVE,
        started_at=datetime(2026, 9, 1, 12, 0, tzinfo=jst),
        next_send_at=datetime(2026, 9, 8, 20, 0, tzinfo=jst),
    )
    db_session.add(reading_reminder)
    db_session.commit()
    db_session.refresh(reading_reminder)

    response = client.post(
        f"/users/me/books/{user_book.book_id}/reminder",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 409

    statement = select(ReadingReminder).where(
        ReadingReminder.user_book_id == user_book.id
    )
    reading_reminders = db_session.scalars(statement).all()

    assert len(reading_reminders) == 1
    assert reading_reminders[0].id == reading_reminder.id
    assert reading_reminders[0].status == ReadingReminderStatus.ACTIVE


def test_set_user_book_reading_reminder_returns_401_without_access_token(book_in_db):
    response = client.post(
        f"/users/me/books/{book_in_db.id}/reminder",
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    "invalid_book_id",
    ["abc", 0, -1],
)
def test_set_user_book_reading_reminder_returns_422_invalid_book_id(
    invalid_book_id, access_token
):
    response = client.post(
        f"/users/me/books/{invalid_book_id}/reminder",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422


def test_set_create_user_book_reading_reminder_returns_conflict_when_database_rejects_duplicate(
    user_book_data, access_token, db_session, registered_user, monkeypatch
):
    user_book = UserBook(
        book_id=user_book_data["book_id"],
        user_id=registered_user.id,
        priority=user_book_data["priority"],
        status=ReadingStatus.READING,
    )

    db_session.add(user_book)
    db_session.commit()
    db_session.refresh(user_book)

    rollback_was_called = False
    original_rollback = Session.rollback

    def record_rollback(session):
        nonlocal rollback_was_called
        rollback_was_called = True
        return original_rollback(session)

    def raise_integrity_error(_session):
        raise IntegrityError(
            "INSERT INTO reading_reminders",
            {},
            Exception("duplicate"),
        )

    with monkeypatch.context() as patch:
        patch.setattr(Session, "commit", raise_integrity_error)
        patch.setattr(Session, "rollback", record_rollback)

        response = client.post(
            f"/users/me/books/{user_book.book_id}/reminder",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert response.status_code == 409
    assert rollback_was_called is True


def test_get_user_book_reading_reminder_status(
    user_book_data, access_token, db_session, registered_user
):
    user_book = UserBook(
        book_id=user_book_data["book_id"],
        user_id=registered_user.id,
        priority=user_book_data["priority"],
        status=ReadingStatus.READING,
    )

    db_session.add(user_book)
    db_session.commit()
    db_session.refresh(user_book)

    jst = ZoneInfo("Asia/Tokyo")
    reading_reminder = ReadingReminder(
        user_book_id=user_book.id,
        status=ReadingReminderStatus.SEND_ACCEPTED,
        started_at=datetime(2026, 9, 1, 12, 0, tzinfo=jst),
        next_send_at=datetime(2026, 9, 8, 20, 0, tzinfo=jst),
    )
    db_session.add(reading_reminder)
    db_session.commit()
    db_session.refresh(reading_reminder)

    response = client.get(
        f"/users/me/books/{user_book.book_id}/reminder",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == reading_reminder.id
    assert response_data["user_book_id"] == reading_reminder.user_book_id
    assert response_data["status"] == reading_reminder.status
    assert reading_reminder.next_send_at == datetime.fromisoformat(
        response_data["next_send_at"]
    )


def test_get_user_book_reading_reminder_status_returns_user_book_not_found_error(
    book_in_db, access_token
):
    response = client.get(
        f"/users/me/books/{book_in_db.id}/reminder",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    response_data = response.json()

    assert response_data["detail"] == "この本は読みたいリストに登録されていません。"


def test_get_user_book_reading_reminder_status_returns_reading_reminder_not_found_error(
    user_book_data, access_token, db_session, registered_user
):
    user_book = UserBook(
        book_id=user_book_data["book_id"],
        user_id=registered_user.id,
        priority=user_book_data["priority"],
        status=ReadingStatus.READING,
    )

    db_session.add(user_book)
    db_session.commit()
    db_session.refresh(user_book)

    response = client.get(
        f"/users/me/books/{user_book.book_id}/reminder",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response_data = response.json()

    assert response.status_code == 404
    assert response_data["detail"] == "この本にはリマインダーが設定されていません。"


@pytest.mark.parametrize("invalid_book_id", ["abc", 0, -1])
def test_get_user_book_reading_reminder_status_returns_invalid_book_id_error(
    invalid_book_id, access_token
):
    response = client.get(
        f"/users/me/books/{invalid_book_id}/reminder",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422


def test_get_user_book_reading_reminder_status_returns_without_access_token_error(
    book_in_db,
):
    response = client.get(f"/users/me/books/{book_in_db.id}/reminder")
    assert response.status_code == 401


def test_get_due_reading_reminders(
    registered_user, book_in_db, user_book_data, db_session
):
    user_book = UserBook(
        book_id=user_book_data["book_id"],
        user_id=registered_user.id,
        priority=user_book_data["priority"],
        status=ReadingStatus.READING,
    )

    db_session.add(user_book)
    db_session.commit()
    db_session.refresh(user_book)

    jst = ZoneInfo("Asia/Tokyo")
    reading_reminder = ReadingReminder(
        user_book_id=user_book.id,
        status=ReadingReminderStatus.ACTIVE,
        started_at=datetime(2026, 9, 1, 12, 0, tzinfo=jst),
        next_send_at=datetime(2026, 9, 8, 20, 0, tzinfo=jst),
    )
    db_session.add(reading_reminder)
    db_session.commit()
    db_session.refresh(reading_reminder)

    current_time = datetime(2026, 9, 8, 20, 3, tzinfo=jst)
    due_reminders = get_due_reading_reminders(current_time, db_session)
    assert len(due_reminders) == 1
    reminder, reading_status, email, title = due_reminders[0]

    assert reminder.id == reading_reminder.id
    assert reading_status == user_book.status
    assert email == registered_user.email
    assert title == book_in_db.title


@pytest.mark.parametrize(
    "non_active_status",
    [
        ReadingReminderStatus.READING_STATUS_CHANGED,
        ReadingReminderStatus.SEND_ACCEPTED,
        ReadingReminderStatus.SEND_FAILED,
    ],
)
def test_get_due_reading_reminders_returns_empty_response_with_non_active_status(
    registered_user, book_in_db, user_book_data, db_session, non_active_status
):
    user_book = UserBook(
        book_id=user_book_data["book_id"],
        user_id=registered_user.id,
        priority=user_book_data["priority"],
        status=ReadingStatus.READING,
    )

    db_session.add(user_book)
    db_session.commit()
    db_session.refresh(user_book)

    jst = ZoneInfo("Asia/Tokyo")
    reading_reminder = ReadingReminder(
        user_book_id=user_book.id,
        status=non_active_status,
        started_at=datetime(2026, 9, 1, 12, 0, tzinfo=jst),
        next_send_at=datetime(2026, 9, 8, 20, 0, tzinfo=jst),
    )
    db_session.add(reading_reminder)
    db_session.commit()
    db_session.refresh(reading_reminder)

    current_time = datetime(2026, 9, 8, 20, 3, tzinfo=jst)
    due_reminders = get_due_reading_reminders(current_time, db_session)

    assert len(due_reminders) == 0


def test_get_due_reading_reminders_returns_empty_response_before_next_send_at(
    registered_user, book_in_db, user_book_data, db_session
):
    user_book = UserBook(
        book_id=user_book_data["book_id"],
        user_id=registered_user.id,
        priority=user_book_data["priority"],
        status=ReadingStatus.READING,
    )

    db_session.add(user_book)
    db_session.commit()
    db_session.refresh(user_book)

    jst = ZoneInfo("Asia/Tokyo")
    reading_reminder = ReadingReminder(
        user_book_id=user_book.id,
        status=ReadingReminderStatus.ACTIVE,
        started_at=datetime(2026, 9, 1, 12, 0, tzinfo=jst),
        next_send_at=datetime(2026, 9, 8, 20, 3, tzinfo=jst),
    )
    db_session.add(reading_reminder)
    db_session.commit()

    current_time = datetime(2026, 9, 8, 20, 0, tzinfo=jst)
    due_reminders = get_due_reading_reminders(current_time, db_session)

    assert len(due_reminders) == 0


def test_process_due_reading_reminder_updates_status_when_user_book_is_not_reading(
    registered_user, book_in_db, user_book_data, db_session
):
    user_book = UserBook(
        book_id=user_book_data["book_id"],
        user_id=registered_user.id,
        priority=user_book_data["priority"],
        status=ReadingStatus.WANT_TO_READ,
    )
    db_session.add(user_book)
    db_session.commit()
    db_session.refresh(user_book)

    jst = ZoneInfo("Asia/Tokyo")
    reading_reminder = ReadingReminder(
        user_book_id=user_book.id,
        status=ReadingReminderStatus.ACTIVE,
        started_at=datetime(2026, 9, 1, 12, 0, tzinfo=jst),
        next_send_at=datetime(2026, 9, 8, 20, 0, tzinfo=jst),
    )
    db_session.add(reading_reminder)
    db_session.commit()
    db_session.refresh(reading_reminder)

    process_due_reading_reminder(
        reading_reminder,
        user_book.status,
        registered_user.email,
        book_in_db.title,
        db_session,
    )

    db_session.refresh(reading_reminder)
    assert reading_reminder.status == ReadingReminderStatus.READING_STATUS_CHANGED


def test_process_due_reading_reminder_updates_status_when_email_is_accepted(
    registered_user, book_in_db, user_book_data, db_session, monkeypatch
):
    captured_email = {}

    def fake_send_reading_reminder_email(to_email, book_title, idempotency_key):
        captured_email.update(
            {
                "to_email": to_email,
                "book_title": book_title,
                "idempotency_key": idempotency_key,
            }
        )

    monkeypatch.setattr(
        reading_reminder_service,
        "send_reading_reminder_email",
        fake_send_reading_reminder_email,
    )

    user_book = UserBook(
        book_id=user_book_data["book_id"],
        user_id=registered_user.id,
        priority=user_book_data["priority"],
        status=ReadingStatus.READING,
    )
    db_session.add(user_book)
    db_session.commit()
    db_session.refresh(user_book)

    jst = ZoneInfo("Asia/Tokyo")
    reading_reminder = ReadingReminder(
        user_book_id=user_book.id,
        status=ReadingReminderStatus.ACTIVE,
        started_at=datetime(2026, 9, 1, 12, 0, tzinfo=jst),
        next_send_at=datetime(2026, 9, 8, 20, 0, tzinfo=jst),
    )
    db_session.add(reading_reminder)
    db_session.commit()
    db_session.refresh(reading_reminder)

    process_due_reading_reminder(
        reading_reminder,
        user_book.status,
        registered_user.email,
        book_in_db.title,
        db_session,
    )

    db_session.refresh(reading_reminder)
    assert reading_reminder.status == ReadingReminderStatus.SEND_ACCEPTED
    assert captured_email["to_email"] == registered_user.email
    assert captured_email["book_title"] == book_in_db.title
    assert captured_email["idempotency_key"] == (
        f"reading-reminder/{reading_reminder.id}/"
        f"{reading_reminder.next_send_at.isoformat()}"
    )


def test_process_due_reading_reminder_updates_status_when_email_send_fails(
    registered_user, book_in_db, user_book_data, db_session, monkeypatch
):
    def fake_send_reading_reminder_email(to_email, book_title, idempotency_key):
        raise EmailSendError

    monkeypatch.setattr(
        reading_reminder_service,
        "send_reading_reminder_email",
        fake_send_reading_reminder_email,
    )

    user_book = UserBook(
        book_id=user_book_data["book_id"],
        user_id=registered_user.id,
        priority=user_book_data["priority"],
        status=ReadingStatus.READING,
    )
    db_session.add(user_book)
    db_session.commit()
    db_session.refresh(user_book)

    jst = ZoneInfo("Asia/Tokyo")
    reading_reminder = ReadingReminder(
        user_book_id=user_book.id,
        status=ReadingReminderStatus.ACTIVE,
        started_at=datetime(2026, 9, 1, 12, 0, tzinfo=jst),
        next_send_at=datetime(2026, 9, 8, 20, 0, tzinfo=jst),
    )
    db_session.add(reading_reminder)
    db_session.commit()
    db_session.refresh(reading_reminder)

    process_due_reading_reminder(
        reading_reminder,
        user_book.status,
        registered_user.email,
        book_in_db.title,
        db_session,
    )

    db_session.refresh(reading_reminder)
    assert reading_reminder.status == ReadingReminderStatus.SEND_FAILED


def test_process_due_reading_reminders_processes_each_due_reminder(
    db_session, monkeypatch
):
    jst = ZoneInfo("Asia/Tokyo")
    current_time = datetime(2026, 9, 8, 20, 5, tzinfo=jst)

    reading_reminder_1 = ReadingReminder(id=10)
    reading_reminder_2 = ReadingReminder(id=11)

    due_reminders = [
        (
            reading_reminder_1,
            ReadingStatus.READING,
            "reader1@example.com",
            "本A",
        ),
        (
            reading_reminder_2,
            ReadingStatus.COMPLETED,
            "reader2@example.com",
            "本B",
        ),
    ]
    captured_calls = []

    def fake_get_due_reading_reminders(received_current_time, received_db):
        assert received_current_time == current_time
        assert received_db is db_session
        return due_reminders

    def fake_process_due_reading_reminder(
        reading_reminder,
        reading_status,
        email,
        title,
        received_db,
    ):
        captured_calls.append(
            (
                reading_reminder,
                reading_status,
                email,
                title,
                received_db,
            )
        )

    monkeypatch.setattr(
        reading_reminder_service,
        "get_due_reading_reminders",
        fake_get_due_reading_reminders,
    )

    monkeypatch.setattr(
        reading_reminder_service,
        "process_due_reading_reminder",
        fake_process_due_reading_reminder,
    )

    reading_reminder_service.process_due_reading_reminders(current_time, db_session)
    assert captured_calls == [
        (
            reading_reminder_1,
            ReadingStatus.READING,
            "reader1@example.com",
            "本A",
            db_session,
        ),
        (
            reading_reminder_2,
            ReadingStatus.COMPLETED,
            "reader2@example.com",
            "本B",
            db_session,
        ),
    ]
