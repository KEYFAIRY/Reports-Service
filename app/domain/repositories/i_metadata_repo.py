from abc import ABC, abstractmethod

class IMetadataRepo(ABC):
    
    @abstractmethod
    async def save_pdf_path(self, uid: str, practice_id: int, pdf_path: str) -> bool:
        """Saves the PDF path for a specific practice ID."""
        pass