from datetime import datetime

from pydantic import BaseModel

from enums import ReadingReminderStatus


class ReadingReminderResponse(BaseModel):
    id: int
    user_book_id: int
    status: ReadingReminderStatus
    next_send_at: datetime
