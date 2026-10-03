from datetime import datetime
from zoneinfo import ZoneInfo

from database import SessionLocal
from services.reading_reminders import process_due_reading_reminders


def main() -> None:
    jst = ZoneInfo("Asia/Tokyo")
    current_time = datetime.now(jst)

    with SessionLocal() as db:
        process_due_reading_reminders(current_time, db)


if __name__ == "__main__":
    main()
