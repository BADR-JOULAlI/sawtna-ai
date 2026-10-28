"""Technical quality signals; these never certify legal accuracy or OCR correctness."""
import hashlib
import unicodedata


def text_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def quality_flags(text: str) -> list[str]:
    flags = []
    if len(text.strip()) < 60:
        flags.append("short_text")
    if any(unicodedata.category(c) == "Cc" and c not in "\n\r\t" for c in text):
        flags.append("control_characters")
    if "\ufffd" in text:
        flags.append("replacement_characters")
    visible = [c for c in text if not c.isspace()]
    if len(visible) >= 60 and sum(c.isalpha() for c in visible) / len(visible) < .45:
        flags.append("low_letter_ratio")
    return flags


def needs_ocr(text: str) -> bool:
    return bool(quality_flags(text))
