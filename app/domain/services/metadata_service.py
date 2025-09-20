import logging
from app.domain.repositories.i_metadata_repo import IMetadataRepo
from app.core.exceptions import (
    ReportsServiceException,
    DatabaseConnectionException,
)

logger = logging.getLogger(__name__)


class MetadataPracticeService:
    """Service for handling metadata related to practices."""

    def __init__(self, metadata_repo: IMetadataRepo):
        self.metadata_repo = metadata_repo

    async def save_pdf_path(self, practice_id: str, pdf_path: str) -> str:
        """Save the PDF path associated with a practice."""
        try:
            saved_path = await self.metadata_repo.save_pdf_path(practice_id, pdf_path)
            logger.info("PDF path saved for practice_id=%s -> %s", practice_id, saved_path)
            return saved_path

        except DatabaseConnectionException as db_err:
            logger.error("Database error while saving PDF path: %s", db_err)
            raise

        except Exception as e:
            logger.exception("Unexpected error in save_pdf_path")
            raise ReportsServiceException(
                f"Unexpected error saving PDF path: {str(e)}"
            )