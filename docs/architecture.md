# System Architecture

## Overview

This project implements a real-time log processing architecture that supports local development, secure configuration, automated deployment, and scalable cloud execution.

The system is designed around Apache Airflow as the orchestration layer, Apache Kafka as the streaming backbone, and Elasticsearch as the analytics and search engine.


## Architecture Layers

The architecture is divided into three logical layers:

### 1. Local Development & Testing

Developers author and validate Airflow DAGs locally using an IDE and a local Apache Airflow instance.  
This layer enables rapid iteration and end-to-end validation before any code is deployed to the cloud environment.


### 2. CI/CD Automation

GitHub Actions provides automated deployment by synchronizing Airflow DAGs and dependency definitions to Amazon S3.

This layer acts as the bridge between local development and the MWAA runtime, ensuring that only validated code is promoted to production.


### 3. Cloud Runtime (AWS MWAA)

AWS Managed Workflows for Apache Airflow (MWAA) serves as the production execution environment.

MWAA continuously loads DAG definitions and dependencies from Amazon S3 and executes workflows according to their schedules or manual triggers.


## Component Interaction

At runtime, the system consists of the following core components:

- **Airflow (MWAA)** — Orchestrates producer and consumer workflows
- **Confluent Kafka** — Acts as the real-time messaging layer for log events
- **Elasticsearch** — Stores and indexes structured log data for analytics and search

Each component is loosely coupled, allowing independent scaling and clear responsibility boundaries.


## Data Flow

The end-to-end data flow follows a streaming pattern:

1. Airflow Producer DAG generates synthetic log events
2. Log messages are published to Kafka topics
3. Airflow Consumer DAG consumes Kafka messages
4. Log data is parsed, normalized, and indexed into Elasticsearch

This design enables real-time ingestion while preserving flexibility for downstream analytics.


## Security Considerations

Sensitive configuration values, such as Kafka credentials and Elasticsearch access details, are stored in AWS Secrets Manager.

![AWS_Secrets](https://github.com/eriiinxxuu/mwaa-kafka-elasticsearch-project/blob/main/Images/aws_secrets.png)

Secrets are retrieved securely at runtime by Airflow tasks, ensuring that credentials are not embedded in source code or configuration files.



## Design Decisions

Several key design decisions guided the architecture:

- **Local-first development**  
  Enables fast iteration and validation without relying on cloud resources.

- **Source-based deployment**  
  Airflow DAGs are deployed as plain Python source files, aligning with MWAA’s native deployment model.

- **Separation of concerns**  
  Log generation, streaming, processing, and analytics are handled by dedicated components.

- **Cloud-managed orchestration**  
  MWAA reduces operational overhead while providing a production-grade Airflow environment.



