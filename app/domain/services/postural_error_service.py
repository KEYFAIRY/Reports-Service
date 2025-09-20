import logging
from typing import List
from app.domain.entities.postural_error import PosturalError
from app.domain.repositories.i_postural_error_repo import IPosturalErrorRepo
from app.core.exceptions import (
    ReportsServiceException,
    DatabaseConnectionException,
)

logger = logging.getLogger(__name__)

class PosturalErrorService:
    """Service for handling postural error operations."""

    def __init__(self, postural_error_repo: IPosturalErrorRepo):
        self.postural_error_repo = postural_error_repo

    async def get_errors_by_practice(self, id_practice: int) -> List[PosturalError]:
        """Get postural errors associated with a specific practice session."""
        
        try:
            errors = await self.postural_error_repo.get_by_practice(id_practice)

            if errors is None:
                logger.info("No postural errors found for practice %s", id_practice)
                return []

            return errors

        except DatabaseConnectionException as db_err:
            logger.error("Database connection error while fetching errors: %s", db_err)
            raise

        except Exception as e:
            logger.exception("Unexpected error in get_errors_by_practice")
            raise ReportsServiceException(
                f"Unexpected error fetching postural errors: {str(e)}"
            )