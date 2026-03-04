"""
Repository interface for session storage.
Follows Repository pattern - domain defines interface, infrastructure implements.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.models.session import Session


class SessionRepository(ABC):
    """Abstract repository for session persistence"""
    
    @abstractmethod
    async def get(self, session_id: str) -> Optional[Session]:
        """Retrieve session by ID"""
        pass
    
    @abstractmethod
    async def save(self, session: Session) -> None:
        """Persist session"""
        pass
    
    @abstractmethod
    async def delete(self, session_id: str) -> None:
        """Delete session"""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[Session]:
        """List all sessions"""
        pass
    
    @abstractmethod
    async def exists(self, session_id: str) -> bool:
        """Check if session exists"""
        pass
