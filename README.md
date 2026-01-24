# Realtime Logs Processing with Apache Airflow (AWS MWAA), Kafka and Elasticsearch

> Apache Airflow (MWAA) · Kafka · Elasticsearch · CI/CD

## 📚 Introduction

This project demonstrates an end-to-end real-time log processing and analytics platform built with **Apache Airflow, Confluent Kafka, and Elasticsearch**.

The system supports local-first development, secure secret management, and automated CI/CD deployment to AWS MWAA using GitHub Actions and Amazon S3.


## 🔍 System Architecture
![system architecture](https://github.com/eriiinxxuu/mwaa-kafka-elasticsearch-project/blob/main/Images/mwaa_system_architecture.png)

The architecture consists of three major layers:
- Local Development & Testing
- CI/CD Automation with GitHub Actions
- Cloud Runtime on Amazon Managed Workflows for Apache Airflow (MWAA)

### 1. Local Development and DAG Workflow Design
Development is performed locally using IDE environment and a local Apache Airflow instance.

Two Airflow DAGs are implemented:
- **Producer DAG** 

Generates synthetic access logs and publishes them to Kafka as the upstream source of the log analytics pipeline.


- **Consumer DAG** 

Consumes Kafka messages, parses and normalizes log data, and indexes structured records into Elasticsearch for analytics.

Both the producer and consumer DAGs are scheduled to run every 5 minutes (`*/5 * * * *`).

On each scheduled run:
- The `logs_producer DAG` generates and publishes **15,000** synthetic log messages to Kafka.
- The `logs_processing_pipeline DAG` reads the latest available messages and indexes the collected batch into Elasticsearch using a bulk write operation.

Both DAGs are configured with `catchup=False`, ensuring that only the most recent scheduling window is executed. \
This prevents historical backfills and aligns with the project’s near real-time log processing model.

### 2. Local Airflow Testing Workflow

Once started successfully:
- DAGs are visible in the Airflow UI
- Producer and consumer workflows are triggered manually
- End-to-end validation is performed:
  - Produce messages → Kafka
  - Verify synthetic logs in the topic of Kafka
  - Consume messages → Elasticsearch
  - Verify indexed logs in Elasticsearch

Only after successful local validation does the code move to the deployment stage.

### 3. CI/CD Pipeline with GitHub Actions
- GitHub automatically detects workflows defined in `.github/workflows/`
- Pushes codes to the `main` branch trigger automated deployment
- DAGs and dependencies are synchronized to Amazon S3
- MWAA automatically refreshes DAGs from the configured S3 paths

### 4. AWS MWAA Runtime Environment
The production workflows run on AWS Managed Workflows for Apache Airflow (MWAA). \
The MWAA environment is configured to load:
- Airflow DAGs from an Amazon S3 bucket
- Python dependencies from requirements.txt
- Secrets securely from AWS Secrets Manager

Once deployed: 
- DAGs automatically appear in the MWAA Airflow UI
- Workflows can be triggered manually or on schedule
- Logs flow through Kafka and are indexed into Elasticsearch

Any code changes pushed to GitHub are automatically synchronized to S3 via GitHub Actions and reflected in the MWAA environment, enabling continuous delivery without manual intervention.

## 🧠 Technologies
- **Apache Airflow**: Workflow orchestration for producing and consuming real-time log data
- **AWS Managed Workflows for Apache Airflow (MWAA)**: Fully AWS managed Apache Airflow runtime in production
- **Apache Kafka (Confluent Cloud)**: Distributed event streaming platform for real-time log ingestion
- **Elasticsearch**: Search and analytics engine for indexing and querying log data
- **AWS S3** — DAG and dependency storage
- **AWS Secrets Manager** — Secure credential management
- **GitHub Actions** — CI/CD automation
- **Python**: Primary language for Airflow DAGs and data processing


## 📝 Documentation

- [System Architecture Details](docs/architecture.md)
- [Producer & Consumer DAG Design](docs/dags.md)
- [Local Development Guide](docs/local-airflow-testing.md)
- [CI/CD pipeline](docs/cicd.md)
- [AWS MWAA Environment](docs/mwaa_env.md) (step-by-step guide 💗)





