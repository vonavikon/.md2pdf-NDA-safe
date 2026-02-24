class BotError(Exception):
    """Base exception for bot errors."""
    user_message: str = "An error occurred"


class InvalidFileFormat(BotError):
    user_message = "Please send a file in .md format"


class FileTooLarge(BotError):
    user_message = "File is too large. Maximum size is 10 MB"


class ConversionError(BotError):
    user_message = "Conversion error. Please check your Markdown syntax"


class ConversionTimeout(BotError):
    user_message = "Conversion timeout. The document may be too complex"
