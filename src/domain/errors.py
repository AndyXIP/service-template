class NotFoundError(Exception):
    """Base exception for "entity not found" across domain resources."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
