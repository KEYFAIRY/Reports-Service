import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer
from app.application.dto.practice_data_dto import PracticeDataDTO
from app.infrastructure.kafka.kafka_message import KafkaMessage
from app.core.config import settings

logger = logging.getLogger(__name__)

MAX_CONCURRENT_PDFS = 3
semaphore = asyncio.Semaphore(MAX_CONCURRENT_PDFS)

async def start_kafka_consumer():
    consumer = AIOKafkaConsumer(
        settings.KAFKA_INPUT_TOPIC,
        bootstrap_servers=settings.KAFKA_BROKER,
        enable_auto_commit=False,
        auto_offset_reset=settings.KAFKA_AUTO_OFFSET_RESET,
        group_id=settings.KAFKA_GROUP_ID,
    )

    try:
        await consumer.start()
        logger.info("Kafka consumer started")
    except Exception as e:
        logger.error(f"Error starting Kafka consumer: {e}", exc_info=True)
        return

    try:
        async for msg in consumer:
            try:
                decoded = msg.value.decode()
                logger.info(f"Received raw message: {decoded}")

                # Parsear el mensaje a KafkaMessage
                data = json.loads(decoded)
                kafka_msg = KafkaMessage(**data)
                logger.info(f"Parsed KafkaMessage: {kafka_msg}")

                # Crear el DTO como antes
                dto = PracticeDataDTO(
                    uid=kafka_msg.uid,
                    practice_id=kafka_msg.practice_id,
                    date=kafka_msg.date,
                    time=kafka_msg.time,
                    scale=kafka_msg.scale,
                    scale_type=kafka_msg.scale_type,
                    num_postural_errors=0,  # Placeholder
                    num_musical_errors=0,   # Placeholder
                    duration=kafka_msg.duration,
                    reps=kafka_msg.reps,
                    bpm=kafka_msg.bpm,
                )
                logger.info(f"Created PracticeDataDTO: {dto}")

            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)

    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped")
