from abc import ABC, abstractmethod
from app.domain.entities.musical_error import MusicalError

class IMusicalErrorRepo(ABC):
    
    @abstractmethod
    async def get_by_practice(self, practice_id: int) -> list[MusicalError]:
        """Gets musical errors by practice ID."""
        pass