from enum import StrEnum


class UserBookListType(StrEnum):
    WANT_TO_READ = "want_to_read"
    COMPLETED = "completed"


class ReadingPriority(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReadingStatus(StrEnum):
    WANT_TO_READ = "want_to_read"
    READING = "reading"
    COMPLETED = "completed"


class BookGenre(StrEnum):
    MANGA = "manga"
    NOVEL = "novel"
    BUSINESS = "business"
    SELF_HELP = "self_help"
    TECHNOLOGY = "technology"
    HUMANITIES = "humanities"
    SCIENCE = "science"
    OTHER = "other"


class ReadingReminderStatus(StrEnum):
    ACTIVE = "active"
    SEND_ACCEPTED = "send_accepted"
    READING_STATUS_CHANGED = "reading_status_changed"
    SEND_FAILED = "send_failed"
