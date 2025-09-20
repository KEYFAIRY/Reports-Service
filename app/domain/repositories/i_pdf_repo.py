from abc import ABC, abstractmethod
from typing import List, Dict
from app.domain.entities.practice import Practice
from app.domain.entities.postural_error import PosturalError
from app.domain.entities.musical_error import MusicalError

class IPDFRepo(ABC):
    @abstractmethod
    async def generate_pdf_content(
        self, 
        practice: Practice, 
        postural_errors: List[PosturalError], 
        musical_errors: List[MusicalError],
        screenshots: Dict[int, str]
    ) -> bytes:
        """Generate PDF content as bytes."""
        pass
    
    @abstractmethod
    async def save_pdf(self, uid: str, filename: str, content: bytes) -> str:
        """Save PDF content and return the file path."""
        pass