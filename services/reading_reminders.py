from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from enums import ReadingReminderStatus, ReadingStatus
from models import Book, ReadingReminder, User, UserBook
from schemas.reading_reminders import ReadingReminderResponse
from services.email import EmailSendError, send_reading_reminder_email


class UserBookNotFoundError(Exception):
    pass


class UserBookNotReadingError(Exception):
    pass


class ReadingReminderAlreadyActiveError(Exception):
    pass


class ReadingReminderNotFoundError(Exception):
    pass


def set_reading_reminder(
    book_id: int, current_user_id: int, db: Session
) -> tuple[ReadingReminderResponse, bool]:
    user_book_statement = select(UserBook).where(
        UserBook.book_id == book_id, UserBook.user_id == current_user_id
    )
    user_book = db.scalar(user_book_statement)

    if user_book is None:
        raise UserBookNotFoundError

    if user_book.status != ReadingStatus.READING:
        raise UserBookNotReadingError

    reading_reminder = user_book.reading_reminder

    if (
        reading_reminder is not None
        and reading_reminder.status == ReadingReminderStatus.ACTIVE
    ):
        raise ReadingReminderAlreadyActiveError

    jst = ZoneInfo("Asia/Tokyo")
    started_at = datetime.now(jst)
    next_send_date = started_at.date() + timedelta(days=7)
    next_send_at = datetime.combine(next_send_date, time(hour=20), tzinfo=jst)

    if reading_reminder is None:
        reading_reminder = ReadingReminder(
            user_book_id=user_book.id,
            status=ReadingReminderStatus.ACTIVE,
            started_at=started_at,
            next_send_at=next_send_at,
        )
        is_created = True
        db.add(reading_reminder)

    elif (
        reading_reminder is not None
        and reading_reminder.status != ReadingReminderStatus.ACTIVE
    ):
        reading_reminder.status = ReadingReminderStatus.ACTIVE
        reading_reminder.started_at = started_at
        reading_reminder.next_send_at = next_send_at
        is_created = False

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ReadingReminderAlreadyActiveError
    db.refresh(reading_reminder)

    reading_reminder_response = ReadingReminderResponse(
        id=reading_reminder.id,
        user_book_id=reading_reminder.user_book_id,
        status=reading_reminder.status,
        next_send_at=reading_reminder.next_send_at,
    )

    return (reading_reminder_response, is_created)


def get_reading_reminder(
    book_id: int, current_user_id: int, db: Session
) -> ReadingReminderResponse:
    user_book_statement = select(UserBook).where(
        UserBook.book_id == book_id, UserBook.user_id == current_user_id
    )
    user_book = db.scalar(user_book_statement)

    if user_book is None:
        raise UserBookNotFoundError

    reading_reminder = user_book.reading_reminder

    if reading_reminder is None:
        raise ReadingReminderNotFoundError

    reading_reminder_response = ReadingReminderResponse(
        id=reading_reminder.id,
        user_book_id=reading_reminder.user_book_id,
        status=reading_reminder.status,
        next_send_at=reading_reminder.next_send_at,
    )

    return reading_reminder_response


def get_due_reading_reminders(current_time: datetime, db: Session):
    due_reminder_statement = (
        select(ReadingReminder, UserBook.status, User.email, Book.title)
        .select_from(ReadingReminder)
        .join(UserBook, ReadingReminder.user_book_id == UserBook.id)
        .join(User, UserBook.user_id == User.id)
        .join(Book, UserBook.book_id == Book.id)
        .where(
            ReadingReminder.status == ReadingReminderStatus.ACTIVE,
            ReadingReminder.next_send_at <= current_time,
        )
    )

    due_reminders = db.execute(due_reminder_statement).all()
    return due_reminders


def process_due_reading_reminder(
    reading_reminder: ReadingReminder,
    reading_status: ReadingStatus,
    email: str,
    title: str,
    db: Session,
):
    if reading_status != ReadingStatus.READING:
        reading_reminder.status = ReadingReminderStatus.READING_STATUS_CHANGED

        db.commit()
        return

    idempotency_key = (
        f"reading-reminder/{reading_reminder.id}/"
        f"{reading_reminder.next_send_at.isoformat()}"
    )

    try:
        send_reading_reminder_email(
            email,
            title,
            idempotency_key,
        )
    except EmailSendError:
        reading_reminder.status = ReadingReminderStatus.SEND_FAILED
    else:
        reading_reminder.status = ReadingReminderStatus.SEND_ACCEPTED
    db.commit()


def process_due_reading_reminders(current_time: datetime, db: Session) -> None:
    due_reminders = get_due_reading_reminders(current_time, db)

    for reading_reminder, reading_status, email, title in due_reminders:
        process_due_reading_reminder(
            reading_reminder,
            reading_status,
            email,
            title,
            db,
        )
