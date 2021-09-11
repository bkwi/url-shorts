import os

REDIS_HOST = 'shorts_redis'
REDIS_PORT = 6379
REDIS_METRICS_QUEUE = 'shorts_metrics'

INFLUXDB_CONFIG = {
    'host': 'influxdb',
    'port': 8086,
    'username': os.getenv('INFLUXDB_USERNAME'),
    'password': os.getenv('INFLUXDB_PASSWORD'),
    'database': os.getenv('INFLUXDB_DATABASE')
}
