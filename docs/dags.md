## Producer & Consumer DAG Design

- **Producer DAG** 

The Producer DAG simulates real-world application traffic by generating synthetic access logs and streaming them to Kafka in real time, serving as the upstream source of the log analytics pipeline. \
Each log entry is formatted into a single text line following a structure similar to common access log formats: 

```text
9.180.123.170 - - [Jan 21 2026, 22:23:40] "DELETE /contact HTTP/1.1" 404 13444 "https://example.com" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
```
Once generated, log messages are published directly to Kafka from within the Airflow task using Kafka producer APIs.

- **Consumer DAG** 

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

All secrets required in DAGs tasks are stored in **AWS Secrets Manager**, ensuring credentials are managed securely and centrally.
