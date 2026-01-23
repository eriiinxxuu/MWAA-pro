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

Once the MWAA environment is ready:

- DAGs should appear automatically in the **Airflow UI**
- Trigger workflows to validate end-to-end execution:
  - Producer DAG → publishes logs to Kafka
  - Consumer DAG → consumes Kafka logs and indexes into Elasticsearch

> 📌 Screenshot: Successful Kafka produce / consume and Elasticsearch indexing results  
> ![Kafka & ES results](Images/<your_kafka_es_result_image>.png)

---

### Step 4 — Querying logs in Elasticsearch

Elasticsearch provides powerful search and aggregation capabilities over indexed log documents.

#### Example 1 — Find logs where `status = 500` and `endpoint = /services`

```json
GET aws-mwaa-production/_search
{
  "query": {
    "bool": {
      "filter": [
        { "term": { "status.keyword": "500" } },
        { "term": { "endpoint.keyword": "/services" } }
      ]
    }
  }
}
