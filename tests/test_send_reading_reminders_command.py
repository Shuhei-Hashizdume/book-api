from datetime import datetime
from zoneinfo import ZoneInfo

import commands.send_reading_reminders as send_reading_reminders_command


def test_main_passes_current_time_and_db_to_processor(monkeypatch):
    jst = ZoneInfo("Asia/Tokyo")
    fixed_current_time = datetime(2026, 10, 2, 20, 5, tzinfo=jst)
    fake_db = object()
    captured = {}

    class FakeDateTime:
        @staticmethod
        def now(timezone):
            captured["timezone"] = timezone
            return fixed_current_time

    class FakeSessionContext:
        def __enter__(self):
            return fake_db

        def __exit__(self, exc_type, exc_value, traceback):
            captured["session_closed"] = True

    def fake_session_local():
        return FakeSessionContext()

    def fake_process_due_reading_reminders(current_time, db):
        captured["current_time"] = current_time
        captured["db"] = db

    monkeypatch.setattr(
        send_reading_reminders_command,
        "datetime",
        FakeDateTime,
    )
    monkeypatch.setattr(
        send_reading_reminders_command,
        "SessionLocal",
        fake_session_local,
    )
    monkeypatch.setattr(
        send_reading_reminders_command,
        "process_due_reading_reminders",
        fake_process_due_reading_reminders,
    )

    send_reading_reminders_command.main()

    assert captured["timezone"].key == "Asia/Tokyo"
    assert captured["current_time"] == fixed_current_time
    assert captured["db"] is fake_db
    assert captured["session_closed"] is True
