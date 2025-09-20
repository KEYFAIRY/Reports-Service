from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.practice import Practice


class IPracticeRepo(ABC):
    @abstractmethod
    async def update_num_postural_errors(self, practice_id: int, num_errors: int) -> Optional[Practice]:
        """Updates the number of postural errors for a given practice ID."""
        pass

    @abstractmethod
    async def update_num_musical_errors(self, practice_id: int, num_errors: int) -> Optional[Practice]:
        """Updates the number of musical errors for a given practice ID."""
        pass