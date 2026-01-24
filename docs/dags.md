# Producer & Consumer DAG Design

### Log Production and Consumption Workflows

> **Producer DAG** 

The Producer DAG simulates real-world application traffic by generating synthetic access logs and streaming them to Kafka in real time, serving as the upstream source of the log analytics pipeline. \
To simulate real-world application traffic, the system includes a `log producer component` that generates synthetic web access logs. \
Logs are programmatically created using the `Faker` library combined with randomized request attributes, allowing the pipeline to be tested without relying on real production data. \
Each generated log entry represents a single HTTP request and includes the following fields: 

- **IP address** – randomly generated IPv4 address
- **Timestamp** – current event time at log generation
- **HTTP method** – `GET`, `POST`, `PUT`, or `DELETE`
- **Request endpoint** – representative API and web paths (e.g. `/api/users`, `/services`)
- **HTTP status code** – covering successful, redirect, client error, and server error scenarios
- **Response size** – simulated payload size in bytes
- **Referrer** – simulated traffic source (e.g. search engines or direct access)
- **User-Agent** – common browser and device signatures


Each log entry is formatted into a single text line following a structure similar to common access log formats: 

```text
9.180.123.170 - - [Jan 21 2026, 22:23:40] "DELETE /contact HTTP/1.1" 404 13444 "https://example.com" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
```
Once generated, log messages are published directly to Kafka from within the Airflow task using Kafka producer APIs.

> **Consumer DAG** 

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

### Scheduling and Message Processing Model

Both workflows are triggered every 5 minutes (`*/5 * * * *`, `catchup=False`).

#### Producer DAG

On each scheduled run, the Producer DAG generates **15,000** synthetic access log messages. \
Log messages are published to Kafka **one message at a time** using the Kafka producer API. \
Although messages are produced individually, they collectively form a logical batch representing a single execution window. \
This approach simulates real-world application traffic, where events are emitted continuously rather than as a single payload.

#### Consumer DAG

The Consumer DAG reads messages from Kafka using a consumer group configured with `auto.offset.reset = latest`.

During each scheduled run:
- Messages are polled sequentially from Kafka
- Parsed log records are accumulated in memory
- Once the batch size reaches **15,000 messages**, the logs are indexed into Elasticsearch using a **bulk write operation**

This design balances streaming ingestion from Kafka with efficient batch indexing into Elasticsearch.

> #### Kafka Offset Management Strategy

The consumer is configured with `auto.offset.reset = latest`, meaning that it starts consuming from the most recent messages available at runtime.
This configuration is intentional and aligns with the project’s goal of validating **near real-time log processing** rather than historical reprocessing. \
The system focuses on consuming logs generated during the current scheduling window, avoiding replay of older messages across DAG executions.
