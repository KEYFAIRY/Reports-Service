import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer
from app.application.dto.practice_data_dto import PracticeDataDTO
from app.core.config import settings
from app.domain.services.metadata_service import MetadataPracticeService
from app.domain.services.musical_error_service import MusicalErrorService
from app.domain.services.postural_error_service import PosturalErrorService
from app.infrastructure.kafka.kafka_message import KafkaMessage
from app.infrastructure.repositories.local_pdf_repo import LocalPDFRepository
from app.infrastructure.repositories.mongo_metadata_repo import MongoMetadataRepo
from app.infrastructure.repositories.mysql_musical_error_repo import MySQLMusicalErrorRepository
from app.infrastructure.repositories.mysql_postural_error_repo import MySQLPosturalErrorRepository

logger = logging.getLogger(__name__)

MAX_CONCURRENT_PDFS = 10
semaphore = asyncio.Semaphore(MAX_CONCURRENT_PDFS)

async def start_kafka_consumer():
    postural_error_repo = MySQLPosturalErrorRepository()
    musical_error_repo = MySQLMusicalErrorRepository()
    metadata_repo = MongoMetadataRepo()
    pdf_repo = LocalPDFRepository()

    postural_error_service = PosturalErrorService(postural_error_repo)
    musical_error_service = MusicalErrorService(musical_error_repo)
    metadata_service = MetadataPracticeService(metadata_repo)
    # TODO: pdf_service = PDFService(pdf_repo)

    # TODO: use_case = GeneratePDFUseCase(
    #    postural_error_service,
    #    musical_error_service,
    #    metadata_service,
    #    pdf_service,
    #)

    consumer = AIOKafkaConsumer(
        settings.KAFKA_INPUT_TOPIC,
        bootstrap_servers=settings.KAFKA_BROKER,
        enable_auto_commit=False,
        auto_offset_reset=settings.KAFKA_AUTO_OFFSET_RESET,
        group_id=None,
    )

    await consumer.start()
    tasks = []
    try:
        logger.info("Kafka consumer started")

        async def process_message(dto: PracticeDataDTO):
            async with semaphore:
                try:
                    #TODO: errors = await use_case.execute(dto)
                    logger.info(f"Processed KafkaMessage with {len(errors)} errors")
                    await consumer.commit()
                except Exception as e:
                    logger.error(f"Error processing message in background: {e}", exc_info=True)

        async for msg in consumer:
            try:
                decoded = msg.value.decode()
                logger.info(f"Received raw message: {decoded}")

                data = json.loads(decoded)
                kafka_msg = KafkaMessage(**data)

                dto = PracticeDataDTO(
                    uid=kafka_msg.uid,
                    practice_id=kafka_msg.practice_id,
                    scale=kafka_msg.scale,
                    scale_type=kafka_msg.scale_type,
                    reps=kafka_msg.reps,
                    bpm=kafka_msg.bpm,
                )

                # Crear la tarea y guardarla en la lista
                task = asyncio.create_task(process_message(dto))
                tasks.append(task)

            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)

    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped")

        if tasks:
            logger.info("Waiting for all background tasks to finish...")
            await asyncio.gather(*tasks)  # Espera que todas las tareas terminen
            logger.info("All background tasks finished.")
