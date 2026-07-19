import re


def validate_text_length(text: str, min_len: int = 1, max_len: int = 150) -> bool:
    """
    Проверяет, соответствует ли длина текста заданным ограничениям.
    """
    if not text:
        return False
    return min_len <= len(text.strip()) <= max_len


def validate_telegram_id(telegram_id: str) -> bool:
    """
    Проверяет, является ли переданная строка корректным Telegram ID (только цифры).
    """
    if not telegram_id:
        return False
    return bool(re.match(r"^\d+$", telegram_id.strip()))
