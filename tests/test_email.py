from services import email as email_service


def test_send_reading_reminder_email(monkeypatch):
    captured_params = {}
    captured_options = {}

    def fake_send(params, options):
        captured_params.update(params)
        captured_options.update(options)

    monkeypatch.setattr(
        email_service.settings,
        "resend_api_key",
        "test-api-key",
    )
    monkeypatch.setattr(
        email_service.resend,
        "api_key",
        None,
    )
    monkeypatch.setattr(
        email_service.resend.Emails,
        "send",
        fake_send,
    )

    email_service.send_reading_reminder_email(
        "reader@example.com",
        "Python入門",
        "reading-reminder/123/2026-09-08T20:00:00+09:00",
    )

    assert email_service.resend.api_key == "test-api-key"
    assert captured_params["from"] == email_service.settings.resend_from_email
    assert captured_params["to"] == "reader@example.com"
    assert captured_params["subject"] == "『Python入門』の読書リマインダー"
    assert captured_params["text"] == (
        "『Python入門』の読書はいかがですか？\n\n読み始めてから1週間が経ちました。"
    )
    assert captured_options["idempotency_key"] == (
        "reading-reminder/123/2026-09-08T20:00:00+09:00"
    )
