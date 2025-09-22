import logging
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload

from app.core.exceptions import DatabaseConnectionException
from app.domain.entities.practice import Practice
from app.domain.repositories.i_practice_repo import IPracticeRepo
from app.infrastructure.database.mysql_connection import mysql_connection
from app.infrastructure.database.models.practice_model import PracticeModel

logger = logging.getLogger(__name__)


class MySQLPracticeRepository(IPracticeRepo):
    """Concrete implementation of IPracticeRepo using MySQL."""

    async def update_num_postural_errors(
        self, practice_id: int, num_errors: int
    ) -> Optional[Practice]:
        try:
            async with mysql_connection.get_async_session() as session:
                stmt = (
                    update(PracticeModel)
                    .where(PracticeModel.id == practice_id)
                    .values(num_postural_errors=num_errors)
                )
                await session.execute(stmt)
                await session.commit()

                # fetch updated row + join con Student
                result = await session.execute(
                    select(PracticeModel)
                    .options(joinedload(PracticeModel.student))
                    .where(PracticeModel.id == practice_id)
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
            raise DatabaseConnectionException(f"Error updating practice: {str(e)}")

    async def update_num_musical_errors(
        self, practice_id: int, num_errors: int
    ) -> Optional[Practice]:
        try:
            async with mysql_connection.get_async_session() as session:
                stmt = (
                    update(PracticeModel)
                    .where(PracticeModel.id == practice_id)
                    .values(num_musical_errors=num_errors)
                )
                await session.execute(stmt)
                await session.commit()

                # fetch updated row + join con Student
                result = await session.execute(
                    select(PracticeModel)
                    .options(joinedload(PracticeModel.student))
                    .where(PracticeModel.id == practice_id)
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
            raise DatabaseConnectionException(f"Error updating practice: {str(e)}")

    def _model_to_entity(self, model: PracticeModel) -> Practice:
        return Practice(
            id=model.id,
            date=model.date,
            time=model.time,
            num_postural_errors=model.num_postural_errors or 0,
            num_musical_errors=model.num_musical_errors or 0,
            duration=model.duration or 0,
            id_student=model.id_student,
            student_name=model.student.name if model.student else None,
            scale="",        # no se consulta, ya viene en el DTO
            scale_type="",   # no se consulta, ya viene en el DTO
            reps=0,          # no se consulta, ya viene del DTO
            bpm=model.bpm,
        )