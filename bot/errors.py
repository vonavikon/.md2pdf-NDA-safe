class BotError(Exception):
    """Base exception for bot errors."""
    user_message: str = "Произошла ошибка"

    def __init__(self, user_message: str | None = None):
        super().__init__(user_message or self.user_message)
        if user_message is not None:
            self.user_message = user_message


class InvalidFileFormat(BotError):
    user_message = "Пожалуйста, отправьте файл в формате .md"


class FileTooLarge(BotError):
    def __init__(self, max_size_mb: int):
        super().__init__(f"Файл слишком большой. Максимальный размер: {max_size_mb} МБ")


class ConversionError(BotError):
    user_message = "Ошибка конвертации. Проверьте синтаксис Markdown"

    def __init__(self, details: str | None = None):
        if details:
            sanitized = " ".join(details.split())
            sanitized = sanitized[:180]
            super().__init__(f"{self.user_message}\nПричина: {sanitized}")
            return
        super().__init__()


class ConversionTimeout(BotError):
    def __init__(self, timeout_seconds: int):
        super().__init__(
            f"Превышено время конвертации ({timeout_seconds} сек). "
            "Возможно, документ слишком сложный"
        )
