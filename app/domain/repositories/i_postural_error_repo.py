from abc import ABC, abstractmethod

from app.domain.entities.postural_error import PosturalError

class IPosturalErrorRepo(ABC):

    @abstractmethod
    async def get_by_practice(self, practice_id: int) -> list[PosturalError]:
        """Gets postural errors by practice ID."""
        pass