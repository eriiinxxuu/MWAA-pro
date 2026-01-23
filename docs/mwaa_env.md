# AWS MWAA Runtime Environment
This section describes the final deployment and runtime validation process after all local testing has been completed and the CI/CD pipeline has been configured.

### 1. Deploying Airflow to AWS MWAA

After successful local validation and GitHub CI/CD workflow setup, the Airflow workflows are deployed to the AWS cloud using **AWS Managed Workflows for Apache Airflow (MWAA)**.

During MWAA environment creation, the following S3 paths must be configured correctly:

- **DAG code** (e.g. `s3://<bucket>/dags/`)
- **Python dependencies** via `requirements.txt` (e.g. `s3://<bucket>/requirements.txt`)

> 📌 Screenshot: MWAA S3 configuration  
> ![MWAA_dag_S3_config](https://github.com/eriiinxxuu/mwaa-kafka-elasticsearch-project/blob/main/Images/airflow_config.png)



### 2. Dependency Compatibility and DAG Parsing

MWAA installs Python dependencies based on the provided `requirements.txt`. It is important to ensure that dependency versions are compatible with the selected Airflow / MWAA runtime version, as incompatible packages may prevent DAGs from being parsed or loaded correctly.

If DAGs fail to appear in the Airflow UI or cannot be parsed, `CloudWatch logs` should be inspected for detailed error messages, such as:
- Missing Python packages
- Version conflicts
- Import errors during DAG parsing

`AWS CloudWatch Logs Insights` can be used to run SQL-like queries against Airflow logs, making it easier to filter, search, and troubleshoot parsing and dependency-related issues in MWAA environments.

> 📌 Screenshot: CloudWatch error logs  
> ![cloudwatch_logs](https://github.com/eriiinxxuu/mwaa-kafka-elasticsearch-project/blob/main/Images/mwaa_cloudwatch_loginsights.png)


### 3. Validating DAG Execution in MWAA

Once the MWAA environment is ready and the DAG code is valid:

> 📌 Screenshot: MWAA Environment is ready!
> ![mwaa_env](https://github.com/eriiinxxuu/mwaa-kafka-elasticsearch-project/blob/main/Images/airflow_env_mwaa.png)

- DAGs should appear automatically in the **Airflow UI**

> 📌 Screenshot: DAGs in airflow
> ![airflow_dag](https://github.com/eriiinxxuu/mwaa-kafka-elasticsearch-project/blob/main/Images/airflow_DAG_mwaa.png)

- Trigger workflows to validate end-to-end execution:
  - Producer DAG → publishes logs to Kafka
  - Consumer DAG → consumes Kafka logs and indexes into Elasticsearch

> 📌 Screenshot: Logs successfully produced to the `AWS-MWAA-Production` Kafka topic
> ![Kafka_logs](https://github.com/eriiinxxuu/mwaa-kafka-elasticsearch-project/blob/main/Images/kafka_overview.png)

> 📌 Screenshot: Logs successfully consumed from Kafka and indexed into Elasticsearch (`aws-mwaa-production` index)
> ![es_index](https://github.com/eriiinxxuu/mwaa-kafka-elasticsearch-project/blob/main/Images/es_messages.png)


### 4. Querying and Analyzing Logs in Elasticsearch

Once logs are indexed into Elasticsearch, powerful search and aggregation capabilities become available for analysis.

Typical use cases include:

#### Example 1 — Find logs where `status = 500` and `endpoint = /services`

```json
GET aws-mwaa-production/_search
{
  "query": {
    "bool": {
      "filter": [
        { "term": { "endpoint.keyword": "/services" } },
        { "term": { "status.keyword": "500" } }
      ]
    }
  },
  "sort": [
    { "timestamp": "desc" }
  ],
  "size": 50
}
```
#### Example 2 — Find top N `endpoints` generating the most errors (`status = 500`)
This aggregation enables quick identification of problematic endpoints and is commonly used for error rate analysis and operational troubleshooting.

```json
GET aws-mwaa-production/_search
{
  "size": 0,
  "query": {
    "term": { "status.keyword": "500" }
  },
  "aggs": {
    "top_endpoints": {
      "terms": {
        "field": "endpoint.keyword",
        "size": 3
      }
    }
  }
}
```

#### Example 3 — Aggregate log documents by time using a date histogram where `status = 500`
This aggregation enables real-time monitoring of error trends and helps identify spikes or anomalies in system behavior.

```json
GET aws-mwaa-production/_search
{
  "size": 0,
  "query": {
    "term": { "status.keyword": "500" }
  },
  "aggs": {
    "per_minute": {
      "date_histogram": {
        "field": "timestamp",
        "fixed_interval": "1m"
      }
    }
  }
}
```
These queries enable real-time observability and analytics over streaming log data.

### 5. Continuous Delivery Behavior

MWAA continuously monitors the configured S3 locations for DAG and dependency updates.
Any subsequent code changes pushed to GitHub are:

- Automatically synchronized to Amazon S3 via GitHub Actions
- Detected by MWAA without manual intervention
- Reflected in the Airflow environment as updated DAG definitions

This setup enables continuous delivery of Airflow workflows while maintaining a clear separation between development, deployment, and runtime execution.

