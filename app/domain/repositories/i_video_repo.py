from abc import ABC, abstractmethod
from typing import List, Dict
from app.domain.entities.postural_error import PosturalError

class IVideoRepo(ABC):
    @abstractmethod
    async def get_video(self, uid: str, practice_id: int) -> str:
        """Retrieve the video file path for the given practice ID."""
        pass
    
    @abstractmethod
    async def extract_screenshots_for_errors(self, uid: str, practice_id: int, postural_errors: List[PosturalError]) -> Dict[int, str]:
        """Extract screenshots for postural errors and return a mapping of error index to screenshot path."""
        pass