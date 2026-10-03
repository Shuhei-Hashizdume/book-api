import resend
from resend.exceptions import ResendError

from config import settings


class EmailSendError(Exception):
    pass


def send_reading_reminder_email(
    to_email: str, book_title: str, idempotency_key: str
) -> None:
    resend.api_key = settings.resend_api_key

    params: resend.Emails.SendParams = {
        "from": settings.resend_from_email,
        "to": to_email,
        "subject": f"『{book_title}』の読書リマインダー",
        "text": (
            f"『{book_title}』の読書はいかがですか？\n\n"
            "読み始めてから1週間が経ちました。"
        ),
    }
    try:
        resend.Emails.send(
            params,
            {
                "idempotency_key": idempotency_key,
            },
        )
    except ResendError as error:
        raise EmailSendError from error
