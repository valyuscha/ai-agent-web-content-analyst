"""
Domain exceptions for business rule violations.
"""


class DomainException(Exception):
    """Base exception for domain errors"""
    pass


class SessionNotFoundError(DomainException):
    """Raised when session does not exist"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(f"Session not found: {session_id}")


class InvalidSourceError(DomainException):
    """Raised when source content is invalid"""
    
    def __init__(self, url: str, reason: str):
        self.url = url
        self.reason = reason
        super().__init__(f"Invalid source {url}: {reason}")


class MaxReflectionRerunsExceeded(DomainException):
    """Raised when reflection limit is reached"""
    
    def __init__(self, session_id: str, max_reruns: int):
        self.session_id = session_id
        self.max_reruns = max_reruns
        super().__init__(f"Session {session_id} exceeded max reflection reruns ({max_reruns})")


class TooManyUrlsError(DomainException):
    """Raised when URL count exceeds limit"""
    
    def __init__(self, count: int, max_count: int):
        self.count = count
        self.max_count = max_count
        super().__init__(f"Too many URLs: {count} (max: {max_count})")


class ContentTooLargeError(DomainException):
    """Raised when content exceeds size limit"""
    
    def __init__(self, size: int, max_size: int):
        self.size = size
        self.max_size = max_size
        super().__init__(f"Content too large: {size} bytes (max: {max_size})")


class SSRFViolationError(DomainException):
    """Raised when URL fails SSRF validation"""
    
    def __init__(self, url: str, reason: str):
        self.url = url
        self.reason = reason
        super().__init__(f"SSRF violation for {url}: {reason}")
