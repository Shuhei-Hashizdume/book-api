from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from dependencies import CurrentUserDep, SessionDep
from models import Insight, UserBook
from schemas.insights import InsightCreate, InsightResponse, InsightUpdate

router = APIRouter(prefix="/users/me/books", tags=["insights"])


@router.post(
    "/{book_id}/insights",
    response_model=InsightResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_insight(
    book_id: int,
    insights_data: InsightCreate,
    db: SessionDep,
    current_user: CurrentUserDep,
):
    statement = select(UserBook).where(
        UserBook.book_id == book_id, UserBook.user_id == current_user.id
    )
    user_book = db.scalar(statement)

    if user_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="本が見つかりません。"
        )

    insight = Insight(
        user_id=user_book.user_id,
        book_id=user_book.book_id,
        content=insights_data.content,
    )

    db.add(insight)
    db.commit()
    db.refresh(insight)

    return InsightResponse(
        id=insight.id,
        content=insight.content,
        book_id=insight.book_id,
        book_title=insight.book.title,
    )


@router.get("/{book_id}/insights", response_model=list[InsightResponse])
def list_insights(book_id: int, current_user: CurrentUserDep, db: SessionDep):
    insight_statement = (
        select(Insight)
        .options(joinedload(Insight.book))
        .where(Insight.user_id == current_user.id, Insight.book_id == book_id)
        .order_by(Insight.id)
    )
    insights = db.scalars(insight_statement).all()
    response_list = []
    for insight in insights:
        insight_response = InsightResponse(
            id=insight.id,
            content=insight.content,
            book_id=insight.book_id,
            book_title=insight.book.title,
        )
        response_list.append(insight_response)

    return response_list


@router.patch("/{book_id}/insights/{insight_id}", response_model=InsightResponse)
def update_insight(
    book_id: int,
    insight_id: int,
    insight_data: InsightUpdate,
    current_user: CurrentUserDep,
    db: SessionDep,
):

    insight_statement = select(Insight).where(
        Insight.user_id == current_user.id,
        Insight.book_id == book_id,
        Insight.id == insight_id,
    )
    insight = db.scalar(insight_statement)

    if insight is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="気づきが見つかりません。"
        )

    insight.content = insight_data.content

    db.commit()
    db.refresh(insight)

    return InsightResponse(
        id=insight.id,
        content=insight.content,
        book_id=insight.book_id,
        book_title=insight.book.title,
    )


@router.delete(
    "/{book_id}/insights/{insight_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_insight(
    book_id: int, insight_id: int, current_user: CurrentUserDep, db: SessionDep
):
    insight_statement = select(Insight).where(
        Insight.user_id == current_user.id,
        Insight.book_id == book_id,
        Insight.id == insight_id,
    )
    insight = db.scalar(insight_statement)

    if insight is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="気づきが見つかりません。",
        )

    db.delete(insight)
    db.commit()
