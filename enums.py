from enum import StrEnum


class ReadingPriority(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReadingStatus(StrEnum):
    WANT_TO_READ = "want_to_read"
    READING = "reading"
    COMPLETED = "completed"
