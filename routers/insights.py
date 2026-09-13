from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from dependencies import CurrentUserDep, SessionDep
from models import Insight, UserBook
from schemas.insights import InsightCreate, InsightResponse, InsightUpdate

router = APIRouter(prefix="/users/me/books", tags=["insights"])


@router.post(
    "/{book_id}/insights",
    response_model=InsightResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_insights(
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

    insight = Insight(user_book_id=user_book.id, content=insights_data.content)

    db.add(insight)
    db.commit()
    db.refresh(insight)

    return insight


@router.get("/{book_id}/insights", response_model=list[InsightResponse])
def read_insights(book_id: int, current_user: CurrentUserDep, db: SessionDep):
    statement = select(UserBook).where(
        UserBook.book_id == book_id, UserBook.user_id == current_user.id
    )
    user_book = db.scalar(statement)

    if user_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="本が見つかりません。"
        )

    insight_statement = (
        select(Insight).where(Insight.user_book_id == user_book.id).order_by(Insight.id)
    )
    insights = db.scalars(insight_statement).all()
    return insights


@router.patch("/{book_id}/insights/{insight_id}", response_model=InsightResponse)
def update_insight(
    book_id: int,
    insight_id: int,
    insight_data: InsightUpdate,
    current_user: CurrentUserDep,
    db: SessionDep,
):
    statement = select(UserBook).where(
        UserBook.book_id == book_id, UserBook.user_id == current_user.id
    )
    user_book = db.scalar(statement)

    if user_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="本が見つかりません。"
        )

    insight_statement = select(Insight).where(
        Insight.user_book_id == user_book.id, Insight.id == insight_id
    )
    insight = db.scalar(insight_statement)

    if insight is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="気づきが見つかりません。"
        )

    insight.content = insight_data.content

    db.commit()
    db.refresh(insight)

    return insight


@router.delete(
    "/{book_id}/insights/{insight_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_insight(
    book_id: int, insight_id: int, current_user: CurrentUserDep, db: SessionDep
):
    statement = select(UserBook).where(
        UserBook.book_id == book_id, UserBook.user_id == current_user.id
    )
    user_book = db.scalar(statement)

    if user_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="本が見つかりません。"
        )

    insight_statement = select(Insight).where(
        Insight.user_book_id == user_book.id, Insight.id == insight_id
    )
    insight = db.scalar(insight_statement)

    if insight is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="気づきが見つかりません。",
        )

    db.delete(insight)
    db.commit()
