from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST, start_http_server
import time
from functools import wraps
import os


kafka_messages_processed = Counter(
    'report_kafka_messages_commited_total',
    'Total Kafka messages processed',
    ['topic', 'status']
)

kafka_messages_polled = Counter(
    'report_kafka_messages_polled_total',
    'Total messages polled from Kafka (before processing)',
    ['topic']
)

report_processing_duration = Histogram(
    'report_processing_duration_seconds',
    'Time to process a video',
    buckets=(2, 4, 6, 8, 10, 15, 20, 25)
)

db_operations = Counter(
    'report_db_operations_total',
    'Total database operations performed by the audio analysis service',
    ['operation', 'database', 'status'] 
)

db_operation_duration = Histogram(
    'report_db_operation_duration_seconds',
    'Duration of database write/read operations',
    ['operation', 'database'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

def start_metrics_server(port: int | None = None):
    port = port or int(os.getenv('PROMETHEUS_PORT', '8017'))
    start_http_server(port)
