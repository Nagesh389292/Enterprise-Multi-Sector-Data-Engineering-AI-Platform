# ADR-001: Selection of Redis Streams for Real-Time Event Ingestion

## Context & Problem Statement
The platform requires a real-time ingestion layer for credit card transactions to support sub-millisecond fraud validation, feature engineering, and model inference.

## Decision Drivers
- Need for sub-millisecond latency for credit card transaction validation.
- Low operational overhead and single-binary local development footprint.
- Built-in pub/sub, consumer groups, and stream replay capability.

## Considered Options
1. **Apache Kafka**: High operational complexity, requires Zookeeper/KRaft, excessive JVM memory overhead for local/free-tier execution.
2. **Redis Streams**: In-memory, sub-millisecond, low footprint, native consumer groups.
3. **RabbitMQ**: AMQP broker, lacks efficient stream offsets for replay.

## Decision Outcome
**Chosen Option: Redis Streams**.
Redis Streams provides memory-speed event ingestion with zero-copy stream slicing, consumer group offset tracking, and simple multi-worker scaling without Kafka's infrastructure tax.
