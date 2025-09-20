from abc import ABC, abstractmethod

class IMetadataRepo(ABC):
    
    @abstractmethod
    async def save_pdf_path(self, uid: str, practice_id: int, pdf_path: str) -> bool:
        """Saves the PDF path for a specific practice ID."""
        pass
    
    @abstractmethod
    async def is_video_and_audio_done(self, uid: str, practice_id: int) -> bool:
        """Checks if both video and audio processing are done for a specific practice ID."""
        pass