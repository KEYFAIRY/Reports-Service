import logging
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, update
from app.core.exceptions import DatabaseConnectionException
from app.domain.entities.practice import Practice
from app.domain.repositories.i_practice_repo import IPracticeRepo
from app.infrastructure.database import mysql_connection
from app.infrastructure.database.models.practice_model import PracticeModel

logger = logging.getLogger(__name__)


class MySQLPracticeRepository(IPracticeRepo):
    """Concrete implementation of IPracticeRepo using MySQL."""

    async def update_num_postural_errors(
        self, practice_id: int, num_errors: int
    ) -> Optional[Practice]:
        session = None
        try:
            session = mysql_connection.get_async_session()
            stmt = (
                update(PracticeModel)
                .where(PracticeModel.id == practice_id)
                .values(num_postural_errors=num_errors)
            )
            await session.execute(stmt)
            await session.commit()

            # fetch updated row
            result = await session.execute(
                select(PracticeModel).where(PracticeModel.id == practice_id)
            )
            model = result.scalar_one_or_none()
            if not model:
                logger.warning(f"No practice found with id={practice_id}")
                return None

            logger.debug(
                f"Updated num_postural_errors={num_errors} for practice_id={practice_id}"
            )
            return self._model_to_entity(model)

        except SQLAlchemyError as e:
            logger.error(
                f"MySQL error updating num_postural_errors for practice_id={practice_id}: {e}",
                exc_info=True,
            )
            if session:
                await session.rollback()
            raise DatabaseConnectionException(f"Error updating practice: {str(e)}")
        finally:
            if session:
                await session.close()

    async def update_num_musical_errors(
        self, practice_id: int, num_errors: int
    ) -> Optional[Practice]:
        session = None
        try:
            session = mysql_connection.get_async_session()
            stmt = (
                update(PracticeModel)
                .where(PracticeModel.id == practice_id)
                .values(num_musical_errors=num_errors)
            )
            await session.execute(stmt)
            await session.commit()

            # fetch updated row
            result = await session.execute(
                select(PracticeModel).where(PracticeModel.id == practice_id)
            )
            model = result.scalar_one_or_none()
            if not model:
                logger.warning(f"No practice found with id={practice_id}")
                return None

            logger.debug(
                f"Updated num_musical_errors={num_errors} for practice_id={practice_id}"
            )
            return self._model_to_entity(model)

        except SQLAlchemyError as e:
            logger.error(
                f"MySQL error updating num_musical_errors for practice_id={practice_id}: {e}",
                exc_info=True,
            )
            if session:
                await session.rollback()
            raise DatabaseConnectionException(f"Error updating practice: {str(e)}")
        finally:
            if session:
                await session.close()

    def _model_to_entity(self, model: PracticeModel) -> Practice:
        return Practice(
            id=model.id,
            date=model.date,
            time=model.time,
            num_postural_errors=model.num_postural_errors or 0,
            num_musical_errors=model.num_musical_errors or 0,
            duration=model.duration or 0,
            id_student=model.id_student,
            scale="",        # not query, already in dto
            scale_type="",   # not query, already in dto
            bpm=model.bpm,
        )
