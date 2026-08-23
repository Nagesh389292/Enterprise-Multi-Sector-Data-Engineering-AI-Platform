# ADR-003: Multi-Engine Storage Strategy (PostgreSQL, SQLite Fallback, BigQuery)

## Context & Problem Statement
Data Marts must be accessible for low-latency web queries (React Command Center) as well as cloud enterprise analytics.

## Decision Drivers
- Operational web queries require relational indexed SQL storage.
- Must support 100% offline local development without requiring an active PostgreSQL instance.
- Must support cloud deployment via BigQuery IaC.

## Decision Outcome
**Chosen Option: Dual-Path Storage Engine with Automatic Graceful Degradation**.
- **PostgreSQL**: Primary operational database engine when `POSTGRES_URL` is available.
- **SQLite Fallback**: Portable local file database (`platform_analytics.db`) used automatically when PostgreSQL is offline.
- **BigQuery**: Terraform-provisioned GCP analytical warehouse target (`enterprise_platform_gold`) for cloud BI queries.
