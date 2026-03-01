class BotError(Exception):
    """Base exception for bot errors."""
    user_message: str = "An error occurred"

    def __init__(self, user_message: str | None = None):
        super().__init__(user_message or self.user_message)
        if user_message is not None:
            self.user_message = user_message


class InvalidFileFormat(BotError):
    user_message = "Please send a file in .md format"


class FileTooLarge(BotError):
    def __init__(self, max_size_mb: int):
        super().__init__(f"File is too large. Maximum size is {max_size_mb} MB")


class ConversionError(BotError):
    user_message = "Conversion error. Please check your Markdown syntax"

    def __init__(self, details: str | None = None):
        if details:
            sanitized = " ".join(details.split())
            sanitized = sanitized[:180]
            super().__init__(f"{self.user_message}\nReason: {sanitized}")
            return
        super().__init__()


class ConversionTimeout(BotError):
    def __init__(self, timeout_seconds: int):
        super().__init__(
            f"Conversion timeout ({timeout_seconds} seconds). "
            "The document may be too complex"
        )
