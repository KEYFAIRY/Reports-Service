from abc import ABC, abstractmethod

class IPDFRepo(ABC):
    
    @abstractmethod
    async def save_pdf(self, uid: str, filename: str, content: bytes) -> str:
        """Saves a PDF"""
        pass