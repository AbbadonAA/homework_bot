class InvalidTokenException(Exception):
    """Исключение - доступность переменных окружения."""

    pass


class InvalidApiExc(Exception):
    """Исключение - корректность ответа API."""

    pass


class EmptyListException(Exception):
    """Исключение - статус работы не изменился."""

    pass


class InvalidResponseExc(Exception):
    """Исключение - status_code API != 200."""

    pass


class InvalidJsonExc(Exception):
    """Исключение - Некорректное декодирование JSON."""

    pass
