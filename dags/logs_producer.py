import random
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from confluent_kafka import Producer
from faker import Faker
import logging
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utilis import get_secret


fake = Faker()
logger = logging.getLogger(__name__)


def generate_log():
    """generate synthetic log"""
    methods = ['GET','POST','PUT','DELETE']
    endpoints = ['/api/users','/home','/about','/contact','/services']
    statuses = [200, 301, 302, 400, 404, 500]

    user_agent = [
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)',
        'Mozilla/5.0 (X11; Linux x86_64)',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]

    referrers = [
        'https://example.com',
        'https://google.com',
        '-',
        'https://bing.com',
        'https://yahoo.com'

    
    ]
    ip = fake.ipv4()
    timestamp = datetime.now().strftime('%b %d %Y, %H:%M:%S')
    method = random.choice(methods)
    endpoint = random.choice(endpoints)
    status = random.choice(statuses)
    user_agent = random.choice(user_agent)
    referrer = random.choice(referrers)
    size = random.randint(1000, 15000) # size of the request
    
    log_entry = (
        f'{ip} - - [{timestamp}] "{method} {endpoint} HTTP/1.1" {status} {size} "{referrer}" "{user_agent}"'
    )
    return log_entry

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')


def produce_logs(**context):
    """ produce log entries into kafka"""
    secrets = get_secret()

    kafka_config = {
        'bootstrap.servers': secrets['kafka_bootstrap_server'],
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': secrets['kafka_username'],
        'sasl.password':secrets['kafka_secret'],
        'session.timeout.ms': 50000

    }
    producer = Producer(kafka_config)
    topic = 'AWS-MWAA-Production'

    for _ in range(15000):
        log = generate_log()
        try: 
            producer.produce(topic, log.encode('utf-8'), on_delivery=delivery_report)
            producer.flush()
        except Exception as e:
            logger.error(f"Failed to produce message: {e}")
            raise e
    logger.info(f"produced 15000 log messages to topic {topic}")
        



default_args = {
    'owner': 'Data Engineer Lab - Erin Xu',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries':1,
    'retry_delay': timedelta(seconds=5)
}

dag = DAG (
    'log_generation_pipeline',
    default_args=default_args,
    description='Generate and produce synthetic logs',
    schedule='*/5 * * * *',
    start_date=datetime(2026, 1, 18),
    catchup=False,
    tags=['logs', 'kafka', 'production']
)

produce_logs_task = PythonOperator(
    task_id='generate_and_produce_logs',
    python_callable=produce_logs,
    dag=dag
)
