import os
import aiofiles
import logging
from app.domain.repositories.i_pdf_repo import IPDFRepo

logger = logging.getLogger(__name__)


class LocalPDFRepository(IPDFRepo):
    """Concrete implementation of IPDFRepo using local file system."""

    def __init__(self, base_dir: str | None = None):
        self.base_dir = base_dir or os.getenv("CONTAINER_PDF_PATH", "/app/storage")
        os.makedirs(self.base_dir, exist_ok=True)

    async def save_pdf(self, uid: str, filename: str, content: bytes) -> str:
        """
        Save a PDF file under path: base_dir/{uid}/reports/{filename}
        """
        user_dir = os.path.join(self.base_dir, uid, "reports")
        os.makedirs(user_dir, exist_ok=True)
        file_path = os.path.join(user_dir, filename)

        try:
            async with aiofiles.open(file_path, "wb") as out_file:
                await out_file.write(content)
            logger.info(f"PDF saved at {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving PDF {filename}: {e}", exc_info=True)
            raise
