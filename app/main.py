from contextlib import asynccontextmanager
import logging
import asyncio

from app.core.config import settings
from app.core.logging import configure_logging
from app.infrastructure.database import mongo_connection, mysql_connection
from app.infrastructure.kafka.kafka_consumer import start_kafka_consumer

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)


async def initialize_databases(retry_delay: int = 5):
    mysql_connected = False
    mongo_connected = False
    attempt = 0
    
    while not (mysql_connected and mongo_connected):

        logger.info(f"Reintentando conexión a BDs (intento {attempt + 1})...")
        await asyncio.sleep(retry_delay)

        attempt += 1
        
        # MySQL
        if not mysql_connected:
            try:
                mysql_connection.mysql_connection.init_engine()
                await mysql_connection.mysql_connection.verify_connection()
                mysql_connected = True
            except Exception as e:
                logger.warning(f"⚠️  MySQL connection failed: {e}")
        
        # MongoDB
        if not mongo_connected:
            try:
                mongo_connection.mongo_connection.connect()
                await mongo_connection.mongo_connection.verify_connection()
                mongo_connected = True
            except Exception as e:
                logger.warning(f"⚠️  MongoDB connection failed: {e}")
    
    logger.info("✅ Todas las conexiones de BD establecidas y verificadas")


async def kafka_consumer_with_retry(retry_delay: int = 5):
    attempt = 0
    
    while True:
        try:
            if attempt > 0:
                logger.info(f"Reintentando iniciar Kafka consumer (intento {attempt + 1})...")
            
            await start_kafka_consumer()
            
            logger.warning("Kafka consumer se detuvo, reiniciando...")
            
        except asyncio.CancelledError:
            logger.info("Kafka consumer task cancelada")
            raise
            
        except Exception as e:
            attempt += 1
            logger.error(f"Error en Kafka consumer (intento {attempt}): {e}", exc_info=True)
            logger.info(f"Esperando {retry_delay}s antes de reintentar...")
            await asyncio.sleep(retry_delay)


@asynccontextmanager
async def lifespan():
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info("=" * 60)

    consumer_task = None

    try:
        # ---------- DB Connections con Reintentos ----------
        logger.info("Inicializando conexiones de base de datos...")
        await initialize_databases(retry_delay=5)

        # ---------- Kafka con Reintentos ----------
        loop = asyncio.get_event_loop()
        consumer_task = loop.create_task(kafka_consumer_with_retry(retry_delay=5))
        logger.info("Kafka consumer wrapper iniciado con reintentos automáticos")
        
        logger.info("=" * 60)
        logger.info("🚀 Servicio iniciado correctamente")
        logger.info("=" * 60)

        yield

    finally:
        # ---------- Shutdown ----------
        logger.info("=" * 60)
        logger.info("Iniciando apagado graceful...")
        logger.info("=" * 60)
        
        if consumer_task:
            consumer_task.cancel()
            try:
                await consumer_task
            except asyncio.CancelledError:
                logger.info("✅ Kafka consumer stopped")

        # Close DBs
        try:
            await mysql_connection.mysql_connection.close_connections()
            await mongo_connection.mongo_connection.close()
            logger.info("✅ Database connections closed")
        except Exception as e:
            logger.exception("❌ Error closing database connections")
        
        logger.info("=" * 60)
        logger.info("✅ Apagado completo")
        logger.info("=" * 60)


async def main():
    async with lifespan():
        while True:
            await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service stopped manually (Ctrl+C)")
    except Exception as e:
        logger.exception("💥 Service crashed with unexpected error")
        raise