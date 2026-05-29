from app.core.utils import attachment_content_disposition


def test_attachment_content_disposition_ascii_fallback() -> None:
    header = attachment_content_disposition('report "Q1".pdf')
    assert "filename=report _Q1_.pdf" in header
    assert "filename*=UTF-8''" in header


def test_attachment_content_disposition_utf8_name() -> None:
    header = attachment_content_disposition("résumé.pdf")
    assert "filename*=" in header
    assert "résumé.pdf" not in header.split("filename=")[1].split(";")[0]
