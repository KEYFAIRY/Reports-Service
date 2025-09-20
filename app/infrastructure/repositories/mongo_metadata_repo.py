import logging
from app.domain.repositories.i_metadata_repo import IMetadataRepo
from app.infrastructure.database import mongo_connection

logger = logging.getLogger(__name__)

class MongoMetadataRepo(IMetadataRepo):
    """Concrete implementation of IMetadataRepo using MongoDB."""

    def __init__(self):
        try:
            self.db = mongo_connection.connect()
            self.users_collection = self.db["users"]
            logger.info("MongoRepo initialized successfully")
        except Exception as e:
            logger.exception("Error initializing MongoRepo")
            raise

    async def save_pdf_path(self, uid: str, practice_id: int, pdf_path: str) -> bool:
        try:
            result = await self.users_collection.update_one(
                {"uid": uid, "practices.id_practice": practice_id},
                {"$set": {"practices.$.report": pdf_path}}
            )
            if result.modified_count == 1:
                logger.info(
                    "Updated report for uid=%s, practice=%s", uid, practice_id
                )
                return True

            logger.warning(
                "No document updated for uid=%s, practice=%s", uid, practice_id
            )
            return False

        except Exception as e:
            logger.exception(
                "Error updating report for uid=%s, practice=%s",
                uid,
                practice_id,
            )
            raise
