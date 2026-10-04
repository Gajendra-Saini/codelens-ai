class CodeLensError(Exception):
    """Base exception for CodeLens application errors."""


class RepositoryError(CodeLensError):
    """Base exception for repository-related errors."""


class InvalidRepositoryUrlError(RepositoryError):
    """Raised when a repository URL is invalid."""


class RepositoryCloneError(RepositoryError):
    """Raised when a repository cannot be cloned or updated."""


class RepositoryNotFoundError(RepositoryError):
    """Raised when a repository is not available locally."""


class GenerationError(CodeLensError):
    """Base exception for generation-related errors."""


class GenerationUnavailableError(GenerationError):
    """Raised when the LLM service is temporarily unavailable."""