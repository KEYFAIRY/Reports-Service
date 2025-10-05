import logging
from typing import List
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from app.domain.repositories.i_musical_error_repo import IMusicalErrorRepo
from app.domain.entities.musical_error import MusicalError
from app.infrastructure.database.models.musical_error_model import MusicalErrorModel
from app.infrastructure.database.mysql_connection import mysql_connection
from app.core.exceptions import DatabaseConnectionException

logger = logging.getLogger(__name__)


class MySQLMusicalErrorRepository(IMusicalErrorRepo):
    """Concrete implementation of IMusicalErrorRepo using MySQL."""

    async def get_by_practice(self, id_practice: int) -> List[MusicalError]:
        try:
            async with mysql_connection.get_async_session() as session:
                result = await session.execute(
                    select(MusicalErrorModel).where(MusicalErrorModel.id_practice == id_practice)
                )
                rows = result.scalars().all()
                logger.debug(
                    f"Fetched {len(rows)} musical errors for practice_id={id_practice}"
                )
                return [self._model_to_entity(row) for row in rows]

        except SQLAlchemyError as e:
            logger.error(
                f"MySQL error listing musical errors for practice_id={id_practice}: {e}",
                exc_info=True
            )
            raise DatabaseConnectionException(f"Error fetching musical errors: {str(e)}")

    def _model_to_entity(self, model: MusicalErrorModel) -> MusicalError:
        return MusicalError(
            id=model.id,
            min_sec=model.min_sec,
            missed_note=model.missed_note,
            id_practice=model.id_practice
        )
