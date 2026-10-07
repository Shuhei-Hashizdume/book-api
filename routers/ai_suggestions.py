from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Response, status

from dependencies import CurrentUserDep, SessionDep
from schemas.ai_suggestion import AISuggestionResponse
from services.ai_suggestion import (
    AISuggestionGenerationError,
    AISuggestionNotFoundError,
    AISuggestionSaveError,
    InsightNotFoundError,
    create_or_update_ai_suggestion,
    delete_ai_suggestion,
    get_ai_suggestion,
)

router = APIRouter(prefix="/users/me/books", tags=["ai_suggestion"])


@router.post(
    "/{book_id}/insights/{insight_id}/ai_suggestion",
    response_model=AISuggestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def set_users_ai_suggestion(
    book_id: Annotated[int, Path(gt=0)],
    insight_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUserDep,
    db: SessionDep,
    response: Response,
):
    try:
        ai_suggestion, is_created = create_or_update_ai_suggestion(
            book_id, insight_id, current_user.id, db
        )
    except InsightNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="気づきが登録されていません。本を読んで気づきを記録しましょう。",
        )
    except AISuggestionGenerationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="外部サーバーとの通信に失敗しました。",
        )
    except AISuggestionSaveError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI提案を保存できませんでした。",
        )

    if not is_created:
        response.status_code = status.HTTP_200_OK

    return ai_suggestion


@router.get(
    "/{book_id}/insights/{insight_id}/ai_suggestion",
    response_model=AISuggestionResponse,
)
def read_users_ai_suggestion(
    book_id: Annotated[int, Path(gt=0)],
    insight_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUserDep,
    db: SessionDep,
):
    try:
        ai_suggestion = get_ai_suggestion(book_id, insight_id, current_user.id, db)
    except AISuggestionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AI提案が保存されていません。"
        )

    return ai_suggestion


@router.delete(
    "/{book_id}/insights/{insight_id}/ai_suggestion",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_users_ai_suggestion(
    book_id: Annotated[int, Path(gt=0)],
    insight_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUserDep,
    db: SessionDep,
):
    try:
        delete_ai_suggestion(book_id, insight_id, current_user.id, db)
    except AISuggestionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AI提案が保存されていません。"
        )
