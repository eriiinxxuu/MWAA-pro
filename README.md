# Realtime Logs Processing with Apache Airflow (AWS MWAA), Kafka and Elasticsearch


## 📚 Introduction

This project demonstrates an end-to-end real-time log processing and analytics platform built with **Apache Airflow, Confluent Kafka, and Elasticsearch**, following modern cloud-native **CI/CD** pipelines and security best practices.

The system enables logs to be produced, streamed, consumed, and indexed in real time, while supporting local development and testing, secure secret management, and automated deployment to AWS Managed Workflows for Apache Airflow (MWAA).

The entire workflow from **local development to cloud execution** is automated using GitHub Actions and Amazon S3, ensuring that any code changes pushed to GitHub are seamlessly propagated to the MWAA environment.


## 🔍 System Architecture
![system architecture](https://github.com/eriiinxxuu/mwaa-kafka-elasticsearch-project/blob/main/Images/mwaa_system_architecture.png)

The architecture consists of three major layers:
- Local Development & Testing
- CI/CD Automation with GitHub Actions
- Cloud Runtime on Amazon Managed Workflows for Apache Airflow (MWAA)

### 1. Local Development & Secure Configuration
Development is performed locally using IDE environment and a local Apache Airflow instance.

Two Airflow DAGs are implemented:
- **Producer DAG** \
The Producer DAG simulates real-world application traffic by generating synthetic access logs and streaming them to Kafka in real time, serving as the upstream source of the log analytics pipeline. \
Each log entry is formatted into a single text line following a structure similar to common access log formats: 

```text
9.180.123.170 - - [Jan 21 2026, 22:23:40] "DELETE /contact HTTP/1.1" 404 13444 "https://example.com" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
```
Once generated, log messages are published directly to Kafka from within the Airflow task using Kafka producer APIs.

- **Consumer DAG** \
Consumes Kafka messages and indexes them into Elasticsearch using bulk writes. However, the Consumer DAG performs a log parsing and normalization step before indexing data into Elasticsearch. \
Kafka messages are received as raw log strings, which are not suitable for structured querying or analytics. To address this, each log entry is parsed using a regular expression that extracts key fields such as IP address, HTTP method, endpoint, status code, response size, referrer, and user-agent. \
A critical part of this transformation is **timestamp** normalization. \
Original log timestamps follow a human-readable format:

```text
Jan 21 2026, 22:23:40
```
Before indexing, timestamps are converted into ISO 8601 format
```text
2026-01-21T22:23:40
```
By normalizing timestamps at the consumer level, the system guarantees that downstream analytics operate on consistent and query-friendly time representations.

### 2. Local Airflow Testing Workflow

