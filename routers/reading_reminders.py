from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Response, status

from dependencies import CurrentUserDep, SessionDep
from schemas.reading_reminders import ReadingReminderResponse
from services.reading_reminders import (
    ReadingReminderAlreadyActiveError,
    ReadingReminderNotFoundError,
    UserBookNotFoundError,
    UserBookNotReadingError,
    get_reading_reminder,
    set_reading_reminder,
)

router = APIRouter(prefix="/users/me/books", tags=["reading-reminders"])


@router.post(
    "/{book_id}/reminder",
    response_model=ReadingReminderResponse,
    status_code=status.HTTP_200_OK,
)
def set_user_book_reading_reminder(
    book_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUserDep,
    db: SessionDep,
    response: Response,
):
    try:
        (reminder_response, is_created) = set_reading_reminder(
            book_id, current_user.id, db
        )
    except UserBookNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="この本は読みたいリストに登録されていません。",
        )
    except UserBookNotReadingError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="読書中の本にのみリマインドを設定できます。",
        )
    except ReadingReminderAlreadyActiveError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="この本にはすでにリマインドが設定されています。",
        )

    if is_created:
        response.status_code = status.HTTP_201_CREATED

    return reminder_response


@router.get("/{book_id}/reminder", response_model=ReadingReminderResponse)
def get_user_book_reading_reminder_status(
    book_id: Annotated[int, Path(gt=0)], current_user: CurrentUserDep, db: SessionDep
):
    try:
        reminder_status_response = get_reading_reminder(book_id, current_user.id, db)
    except UserBookNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="この本は読みたいリストに登録されていません。",
        )
    except ReadingReminderNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="この本にはリマインダーが設定されていません。",
        )
    return reminder_status_response
