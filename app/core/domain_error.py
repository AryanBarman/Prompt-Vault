class DomainError(Exception):
    """Base class for all domain specific errors"""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class PromptNotFound(DomainError):
    def __init__(self, prompt_id: int):
        super().__init__(
            f"Prompt with id {prompt_id} not found",
            status_code=404
        )

class VersionNotFound(DomainError):
    def __init__(self, version_id: int):
        super().__init__(
            f"Version with id {version_id} not found",
            status_code=404
        )

class UnauthorizedActionError(DomainError):
    def __init__(self, action: str = "perform this action"):
        super().__init__(
            f"You do not have permission to {action}",
            status_code=403
        )