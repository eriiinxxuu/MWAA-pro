# Realtime Logs Processing with Apache Airflow (AWS MWAA), Kafka and Elasticsearch


## Introduction

This project demonstrates an end-to-end real-time log processing and analytics platform built with **Apache Airflow, Kafka, and Elasticsearch**, following modern cloud-native **CI/CD** pipelines and security best practices.

The system enables logs to be produced, streamed, consumed, and indexed in real time, while supporting local development and testing, secure secret management, and automated deployment to AWS Managed Workflows for Apache Airflow (MWAA).

The entire workflow from **local development to cloud execution** is automated using GitHub Actions and Amazon S3, ensuring that any code changes pushed to GitHub are seamlessly propagated to the MWAA environment.


## System Architecture
<!-- ![mwaa_system_architecture.png] -->

The architecture consists of three major layers:
- Local Development & Testing
- CI/CD Automation with GitHub Actions
- Cloud Runtime on Amazon Managed Workflows for Apache Airflow (MWAA)