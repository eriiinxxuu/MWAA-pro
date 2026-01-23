# Local Airflow Testing Workflow

Startup Sequence

```text
airflow db migrate
airflow dag-processor
airflow scheduler
airflow api-server -p 8080
```

Once started successfully:
- DAGs are visible in the Airflow UI
- Producer and consumer workflows are triggered manually
- End-to-end validation is performed:
  - Produce messages → Kafka
  - Verify synthetic logs in the topic of Kafka
  - Consume messages → Elasticsearch
  - Verify indexed logs in Elasticsearch

Only after successful local validation does the code move to the deployment stage.
