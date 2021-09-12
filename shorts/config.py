import os

SHORT_ID_LENGTH = 7
CACHE_TTL = 30

REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PORT = 6379
REDIS_METRICS_QUEUE = 'shorts_metrics'

POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
POSTGRES_HOST = os.environ['POSTGRES_HOST']

POSTGRES_URI = f'postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/shorts_db'

METRICS_BATCH_SIZE = 10
METRICS_BATCH_INTERVAL = 10

INFLUXDB_CONFIG = {
    'host': 'influxdb',
    'port': 8086,
    'username': os.getenv('INFLUXDB_USERNAME'),
    'password': os.getenv('INFLUXDB_PASSWORD'),
    'database': os.getenv('INFLUXDB_DATABASE')
}
