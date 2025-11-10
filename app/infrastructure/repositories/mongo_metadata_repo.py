import logging
from app.domain.repositories.i_metadata_repo import IMetadataRepo
from app.infrastructure.database.mongo_connection import mongo_connection
from app.infrastructure.monitoring import metrics

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
                metrics.db_operations.labels(
                        operation='Update', 
                        database='MongoDB',
                        status = 'success'
                    ).inc()
                logger.info(
                    "Updated report for uid=%s, practice=%s", uid, practice_id
                )
                return True

            metrics.db_operations.labels(
                        operation='Update', 
                        database='MongoDB',
                        status = 'error'
                    ).inc()
            logger.warning(
                "No document updated for uid=%s, practice=%s", uid, practice_id
            )
            return False

        except Exception as e:
            metrics.db_operations.labels(
                        operation='Update', 
                        database='MongoDB',
                        status = 'error'
                    ).inc()
            logger.exception(
                "Error updating report for uid=%s, practice=%s",
                uid,
                practice_id,
            )
            raise
    
    async def is_video_and_audio_done(self, uid: str, practice_id: int) -> bool:
        """Checks if both video and audio processing are done for a specific practice ID."""
        try:
            # Query to find the specific practice and check if both audio_done and video_done are true
            result = await self.users_collection.find_one(
                {
                    "uid": uid,
                    "practices": {
                        "$elemMatch": {
                            "id_practice": practice_id,
                            "audio_done": True,
                            "video_done": True
                        }
                    }
                },
                {"practices.$": 1}  # Project only the matching practice
            )
            metrics.db_operations.labels(
                        operation='Read', 
                        database='MongoDB',
                        status = 'success'
                    ).inc()
            
            if result and "practices" in result and len(result["practices"]) > 0:
                practice = result["practices"][0]
                logger.info(
                    "Video and audio processing completed for uid=%s, practice=%s",
                    uid,
                    practice_id
                )
                return True
            else:
                logger.debug(
                    "Video and/or audio processing not completed for uid=%s, practice=%s",
                    uid,
                    practice_id
                )
                return False

        except Exception as e:
            metrics.db_operations.labels(
                        operation='Update', 
                        database='MongoDB',
                        status = 'error'
                    ).inc()
            logger.exception(
                "Error checking video and audio status for uid=%s, practice=%s",
                uid,
                practice_id,
            )
            raise