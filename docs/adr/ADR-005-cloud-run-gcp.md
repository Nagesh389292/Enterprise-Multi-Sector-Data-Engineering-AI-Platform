# ADR-005: GCP Cloud Run Container Serverless Architecture

## Context & Problem Statement
The application backend requires containerized cloud hosting with automatic scale-to-zero capability to eliminate idle cloud costs.

## Decision Drivers
- Scale-to-zero when no HTTP traffic is received.
- Native integration with Docker containers and Terraform IaC.
- Avoids GKE / Kubernetes cluster management overhead and fixed hourly node fees.

## Decision Outcome
**Chosen Option: GCP Cloud Run (`enterprise-platform-api`)**.
Cloud Run provides fully managed serverless container execution with zero cost at rest, making it ideal for demonstration and production deployment without ongoing cluster expense.
