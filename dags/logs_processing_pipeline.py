import re
from airflow import DAG
from datetime import datetime, timedelta
from airflow.providers.standard.operators.python import PythonOperator
from confluent_kafka import Consumer, KafkaException
from elasticsearch import Elasticsearch
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utilis import get_secret
from elasticsearch import helpers


logger = logging.getLogger(__name__)

def parse_log_entry(log_entry):
    log_pattern = log_pattern = (
    r'^(?P<ip>\d{1,3}(?:\.\d{1,3}){3}) - - '
    r'\[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>\w+) (?P<endpoint>\S+) HTTP/1\.1" '
    r'(?P<status>\d{3}) (?P<size>\d+) '
    r'"(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)"'
)


    match = re.match(log_pattern, log_entry)
    if not match:
        logger.warning(f"Failed to parse log entry: {log_entry}")
        return None
    # reach log entry as a dictionary
    data =  match.groupdict()

    try:
        # convert timestamp to ISO 8601 format: 2026-01-17T21:37:17
        parsed_timestamp = datetime.strptime(data['timestamp'], '%b %d %Y, %H:%M:%S')
        data['timestamp']= parsed_timestamp.isoformat()
    except ValueError as e:
        logger.error(f"Timestamp parsing error: {data['timestamp']}")
        return None
    return data
    
def consume_index_logs():
        
        """ consume log entries from kafka"""
        secrets = get_secret()
        consumer_config = {
            'bootstrap.servers': secrets['kafka_bootstrap_server'],
            'security.protocol': 'SASL_SSL',
            'sasl.mechanisms': 'PLAIN',
            'sasl.username': secrets['kafka_username'],
            'sasl.password':secrets['kafka_secret'],
            'group.id': 'log_consumer_group',
            'auto.offset.reset': 'latest'
        }

        #Elasticsearch configuration
        es_config = {
                'hosts': [secrets['elasticsearch_URL']],
                'api_key': secrets['elasticsearch_API_Key']
        }

        consumer = Consumer(consumer_config)
        es = Elasticsearch(**es_config)
        topic = 'AWS-MWAA-Production'
        consumer.subscribe([topic])

        try:
            index_name = topic.lower()
            if not es.indices.exists(index=index_name):
                es.indices.create(index=index_name)
                logger.info(f"Created index {index_name} in Elasticsearch")
        except Exception as e:
            logger.error(f"Error creating index {index_name}: {e}")
            raise e
        logs=[]
        try:
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    break
                if msg.error():
                    if msg.error().code() == KafkaException._PARTITION_EOF:
                        logger.info(f"End of partition reached {msg.topic()} [{msg.partition()}]")
                        break
                    raise KafkaException(msg.error())
                
                log_entry = msg.value().decode('utf-8')
                parsed_log = parse_log_entry(log_entry)
                if parsed_log:
                    logs.append(parsed_log)

            # index when all logs are collected
            if len(logs) >= 15000:
                
                    # each log is written as a document into an Elasticsearch index.
                    # can [create], [delete], [index] or [update]
                actions = [
                    {
                        '_op_type': 'create',
                        '_index': index_name,
                        '_source': log
                    }
                    for log in logs
                ]
                # bulk-writes all logs defined in actions into the Elasticsearch index.
                sucess, failed = helpers.bulk(es, actions, refresh=True)
                logger.info(f"Indexed {sucess} logs, {len(failed)} failed")
                # reset logs
                logs=[]

        except Exception as e:
            logger.error(f"Failed to index log:{e}")
            raise e
        try:
            # index any remaining logs
            if logs:
                actions = [
                    {
                        '_op_type': 'create',
                        '_index': index_name,
                        '_source': log
                    }
                            
                    for log in logs
                ]
                        
                sucess, failed = helpers.bulk(es, actions, refresh=True)
                logger.info(f"Indexed remaining {sucess} logs, {len(failed)} failed")

        except Exception as e:
            logger.error(f"Failed to index remaining logs:{e}")
            raise e
             

default_args = {
    'owner': 'Data Engineer Lab - Erin Xu',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries':1,
    'retry_delay': timedelta(seconds=5)
}

dag = DAG (
    'log_consumer_pipeline',
    default_args=default_args,
    description='Consume and Index synthetic logs',
    schedule='*/5 * * * *',
    start_date=datetime(2026, 1, 18),
    catchup=False,
    tags=['elasticsearch', 'kafka', 'logs']
)

consume_logs_task = PythonOperator(
    task_id='consume_and_index_logs',
    python_callable=consume_index_logs,
    dag=dag
)