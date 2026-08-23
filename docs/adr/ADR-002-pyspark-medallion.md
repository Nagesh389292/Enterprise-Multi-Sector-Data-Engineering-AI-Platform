# ADR-002: PySpark 4.2.0 Medallion Data Lakehouse Architecture

## Context & Problem Statement
The platform must transform multi-sector raw data into aggregated analytical Gold Marts while demonstrating production-grade Data Lakehouse patterns.

## Decision Drivers
- Industrial standard 3-tier Lakehouse pattern (Bronze raw $\rightarrow$ Silver cleaned $\rightarrow$ Gold aggregated).
- Demonstrates distributed SQL window functions, schema enforcement, and Parquet columnar storage.
- Datasets in development are benchmark-sized (~1,000–3,000 rows) for zero-cost local execution, but code must scale to petabytes without architectural rewrites.

## Decision Outcome
**Chosen Option: PySpark 4.2.0 with Parquet Lakehouse Storage**.
PySpark provides declarative DataFrame API, window operations, and Parquet serialization. Benchmark datasets are processed locally in standalone SparkSession mode to guarantee 100% free reproducibility while retaining enterprise PySpark transformation logic.
