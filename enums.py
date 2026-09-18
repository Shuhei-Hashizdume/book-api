from enum import StrEnum


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
