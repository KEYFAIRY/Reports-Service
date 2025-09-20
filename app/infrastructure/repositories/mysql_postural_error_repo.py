import logging
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from app.core.exceptions import DatabaseConnectionException
from app.domain.entities.postural_error import PosturalError
from app.domain.repositories.i_postural_error_repo import IPosturalErrorRepo
from app.infrastructure.database import mysql_connection
from app.infrastructure.database.models.postural_error_model import PosturalErrorModel

logger = logging.getLogger(__name__)

class MySQLPosturalErrorRepository(IPosturalErrorRepo):
    """Concrete implementation of IPosturalErrorRepo using MySQL."""
    
    async def get_by_practice(self, id_practice: int) -> List[PosturalError]:
        session = None
        try:
            session = mysql_connection.get_async_session()
            result = await session.execute(
                select(PosturalErrorModel).where(PosturalErrorModel.id_practice == id_practice)
            )
            rows = result.scalars().all()
            logger.debug(f"Fetched {len(rows)} postural errors for practice_id={id_practice}")
            return [self._model_to_entity(row) for row in rows]
        except SQLAlchemyError as e:
            logger.error(
                f"MySQL error listing postural errors for practice_id={id_practice}: {e}",
                exc_info=True
            )
            raise DatabaseConnectionException(f"Error fetching postural errors: {str(e)}")
        finally:
            if session:
                await session.close()
    
    def _model_to_entity(self, model: PosturalErrorModel) -> PosturalError:
        return PosturalError(
            id=model.id,
            min_sec_init=model.min_sec_init,
            min_sec_end=model.min_sec_end,
            explication=model.explication,
            id_practice=model.id_practice
        )