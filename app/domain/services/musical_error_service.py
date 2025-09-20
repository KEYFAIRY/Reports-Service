import logging
from typing import List
from app.domain.entities.musical_error import MusicalError
from app.domain.repositories.i_musical_error_repo import IMusicalErrorRepo
from app.core.exceptions import (
    ReportsServiceException,
    DatabaseConnectionException,
)

logger = logging.getLogger(__name__)

class MusicalErrorService:
    """Service for handling musical error operations."""

    def __init__(self, musical_error_repo: IMusicalErrorRepo):
        self.musical_error_repo = musical_error_repo

    async def get_errors_by_practice(self, id_practice: int) -> List[MusicalError]:
        """Get musical errors associated with a specific practice session."""

        try:
            errors = await self.musical_error_repo.get_by_practice(id_practice)

            if errors is None:
                logger.info("No musical errors found for practice %s", id_practice)
                return []

            return errors

        except DatabaseConnectionException as db_err:
            logger.error("Database connection error while fetching errors: %s", db_err)
            raise

        except Exception as e:
            logger.exception("Unexpected error in get_errors_by_practice")
            raise ReportsServiceException(
                f"Unexpected error fetching musical errors: {str(e)}"
            )