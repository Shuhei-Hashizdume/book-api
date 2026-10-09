from openai import APIError, OpenAI
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from config import settings
from models import AISuggestion, Book, Insight
from schemas.ai_suggestion import AISuggestionOutput


class InsightNotFoundError(Exception):
    pass


class AISuggestionGenerationError(Exception):
    pass


class AISuggestionSaveError(Exception):
    pass


class AISuggestionNotFoundError(Exception):
    pass


def get_ai_suggestion_context(
    book_id: int, insight_id: int, current_user_id: int, db: Session
):
    context_statement = (
        select(
            Insight.content,
            Book.title,
            Book.author,
        )
        .select_from(Insight)
        .join(Book, Insight.book_id == Book.id)
        .where(
            Insight.id == insight_id,
            Insight.user_id == current_user_id,
            Insight.book_id == book_id,
        )
    )

    context = db.execute(context_statement).mappings().one_or_none()

    if context is None:
        raise InsightNotFoundError

    return context


def generate_ai_suggestion(content: str, title: str, author: str) -> AISuggestionOutput:
    client = OpenAI(api_key=settings.openai_api_key)
    input_text = f"書籍名: {title}\n著者:{author}\n気づき:{content}"
    instructions = """読者が本から得た気づきを整理・深掘りし、仕事や日常生活での具体的な活かし方を示してください。そのうえで、今日〜数日以内に実行できる小さな行動を1つ提案してください。
元の気づきの意味を変えず、読者が書いていない事情や心理を決めつけないでください。
回答は、以下の4項目に沿って生成してください。

1. `clarified_insight`
   - 読者が記録した気づきを、意味を変えずにわかりやすく整理してください。
   - 読者自身が「自分は何に気づいたのか」を明確に理解できる内容にしてください。
   - 80文字程度
   - 1〜2文

2. `deep_dive`
   - その気づきがなぜ重要なのか、どのような意味や背景があるのかを少し具体化してください。
   - 元の気づきから離れすぎず、理解を一段深める内容にしてください。
   - 読者が書いていない事情や心理を推測・断定しないでください。
   - 150文字程度

3. `practical_application`
   - その気づきを仕事や日常生活など、現実のどのような場面で活かせるかを具体的に示してください。
   - 抽象的な一般論ではなく、実際の場面をイメージできる内容にしてください。
   - 100文字程度

4. `next_action`
   - その気づきを実際の行動につなげるために、今日〜数日以内に実行できる小さな行動を提案してください。
   - 無理なく始められる、具体的な行動にしてください。
   - 行動の提案は必ず1つだけにしてください。
   - 「意識する」「頑張る」などの抽象的な表現だけで終わらせないでください。
   - 80文字程度

全体を通して、必要以上に長い説明や説教調の表現は避けてください。
AI自身の意見を主役にせず、あくまで読者が記録した気づきを整理し、理解を深め、現実の行動につなげることを目的としてください。

回答には、読者の気づきの整理・深掘り・具体的な活用方法・次の行動に直接役立つ内容だけを含めてください。
AI側の生成方針、判断理由、情報不足についての断り書きは含めないでください。
「どの場面か分からないため」「情報がないため控える」などの説明は書かず、与えられた気づきから無理なく言える内容を提示してください"""

    try:
        response = client.responses.parse(
            model=settings.openai_model,
            instructions=instructions,
            input=input_text,
            text_format=AISuggestionOutput,
        )
    except APIError:
        raise AISuggestionGenerationError

    suggestion = response.output_parsed

    if suggestion is None:
        raise AISuggestionGenerationError

    return suggestion


def create_or_update_ai_suggestion(
    book_id: int, insight_id: int, current_user_id: int, db: Session
) -> tuple[AISuggestion, bool]:
    context = get_ai_suggestion_context(book_id, insight_id, current_user_id, db)
    suggestion = generate_ai_suggestion(
        content=context["content"], title=context["title"], author=context["author"]
    )

    ai_suggestion_statement = select(AISuggestion).where(
        AISuggestion.insight_id == insight_id
    )
    ai_suggestion = db.scalar(ai_suggestion_statement)

    if ai_suggestion is not None:
        ai_suggestion.clarified_insight = suggestion.clarified_insight
        ai_suggestion.deep_dive = suggestion.deep_dive
        ai_suggestion.practical_application = suggestion.practical_application
        ai_suggestion.next_action = suggestion.next_action

        is_created = False
    else:
        ai_suggestion = AISuggestion(
            insight_id=insight_id,
            clarified_insight=suggestion.clarified_insight,
            deep_dive=suggestion.deep_dive,
            practical_application=suggestion.practical_application,
            next_action=suggestion.next_action,
        )
        is_created = True
        db.add(ai_suggestion)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise AISuggestionSaveError

    db.refresh(ai_suggestion)

    return (ai_suggestion, is_created)


def get_ai_suggestion(
    book_id: int, insight_id: int, current_user_id: int, db: Session
) -> AISuggestion:
    statement = (
        select(AISuggestion)
        .join(Insight, Insight.id == AISuggestion.insight_id)
        .where(
            AISuggestion.insight_id == insight_id,
            Insight.book_id == book_id,
            Insight.user_id == current_user_id,
        )
    )

    ai_suggestion = db.scalar(statement)

    if ai_suggestion is None:
        raise AISuggestionNotFoundError

    return ai_suggestion


def delete_ai_suggestion(
    book_id: int, insight_id: int, current_user_id: int, db: Session
) -> None:
    ai_suggestion = get_ai_suggestion(book_id, insight_id, current_user_id, db)

    db.delete(ai_suggestion)
    db.commit()
