from utils.validators import validate_text_length, validate_telegram_id


def test_validate_text_length_valid():
    """Тест валидных значений длины текста."""
    assert validate_text_length("Привет", min_len=2, max_len=10) is True
    assert validate_text_length("  Пробелы спереди и сзади  ", min_len=5, max_len=30) is True


def test_validate_text_length_invalid():
    """Тест некорректных значений длины текста (слишком короткий/длинный)."""
    assert validate_text_length("", min_len=1, max_len=5) is False
    assert validate_text_length("Привет, Нихао-тян!", min_len=1, max_len=5) is False
    assert validate_text_length("   ", min_len=1, max_len=5) is False  # Только пробелы


def test_validate_telegram_id_valid():
    """Тест корректных ID пользователя (состоят только из цифр)."""
    assert validate_telegram_id("123456789") is True
    assert validate_telegram_id("  987654321  ") is True  # С пробелами по бокам


def test_validate_telegram_id_invalid():
    """Тест некорректных ID пользователя (содержат символы или пустые)."""
    assert validate_telegram_id("1234a5678") is False  # Содержит буквы
    assert validate_telegram_id("-12345678") is False  # Отрицательное число
    assert validate_telegram_id("12.34567") is False  # С точкой
    assert validate_telegram_id("") is False
    assert validate_telegram_id("   ") is False
