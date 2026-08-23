import os
import win32com.client

os.makedirs('docs/media', exist_ok=True)
speaker = win32com.client.Dispatch('SAPI.SpVoice')

# Set comfortable, human-like speaking rate
speaker.Rate = -1

stream = win32com.client.Dispatch('SAPI.SpFileStream')
audio_path = os.path.abspath('docs/media/demo_narration.wav')
stream.Open(audio_path, 3, False)
speaker.AudioOutputStream = stream

story_script = """
Welcome to this engineering walkthrough of the Enterprise Multi-Sector Data Engineering, Machine Learning, Business Intelligence, and AI Copilot Platform. 

Section 1: Introduction and Business Context.
Why do modern enterprises need a multi-sector data engineering and AI platform? In production environments, data is split across silos—financial transactions, healthcare telemetry, clinical records, insurance claims, and retail sales. To make real-time decisions, leadership needs unified ingestion, strict data quality, and secure AI capabilities without compromising auditability. This platform unifies six distinct industry sectors into a single production-grade pipeline.

Section 2: End-to-End System Architecture.
Let's trace how data flows through the complete system architecture. Raw streams from Alpha Vantage stock quotes, OpenAQ air quality data, and economic indicators enter a three-stage PySpark Medallion Lakehouse. Raw data is stored in Bronze, validated and cleaned in Silver with malformed records routed to quarantine, and aggregated into Gold sector data marts. These Gold marts synchronize to Databricks Delta Lake, PostgreSQL, SQLite, and Apache Superset BI. When users ask natural language questions, their queries are evaluated by an Agentic Router, dispatched to Google Gemini 2.5 Flash or OxAlpha via OpenRouter Gateway, and protected by an AST SQL security parser before executing against the data layer.

Section 3: Data Engineering and PySpark Medallion Pipeline.
In the Data Engineering core, raw data enters Bronze storage attached with ingestion timestamps, metadata provenance, and UUID primary keys. The Silver stage enforces schema validation rules; records failing quality assertions are isolated in data quarantine for compliance auditing. Gold data marts summarize domain key performance indicators—credit card fraud scores, banking default risks, hospital bed occupancy rates, clinical readmission risks, and retail gross revenue totals.

Section 4: Databricks SQL Synchronization and Reconciliation.
The critical feature here is not simply loading data into Databricks. The platform actively verifies that the local Gold data marts and Databricks Delta tables agree. Automated reconciliation scripts query Databricks SQL Warehouse 1f1403d78bfa0404 to compare row counts and metric totals. Across all six sectors, the reconciliation achieved 100 percent row matching and exact metric alignment, confirming 0.00 percent data variance across the lakehouse.

Section 5: Machine Learning and MLOps Suite.
Beyond static analytics, the predictive analytics engine turns this data platform into an intelligence platform. We train multi-sector models across XGBoost, LightGBM, Random Forest, Logistic Regression, and PyTorch Autoencoders. Models are versioned in the MLflow model registry with champion model selection. Explainable AI is powered by SHAP TreeExplainer, revealing the top 3 driver reasons behind every flagged transaction anomaly, while Population Stability Index continuously monitors feature distribution drift over time.

Section 6: Multi-Tier AI Copilot Gateway and AST Security.
Now the platform moves from analytics to natural language interaction. A business user does not need to write SQL. They can simply ask a question in natural language. The Agentic Router prioritizes Google Gemini 2.5 Flash as Tier 1, OxAlpha via OpenRouter Gateway as Tier 2 with live HTTP 200 verification, and an offline deterministic analytics engine as Tier 3 fallback. Legacy Ollama daemons have been completely purged. To guarantee security, every generated Text-to-SQL query passes through a sqlglot AST parser that asserts the query root is strictly a SELECT statement, preventing SQL injection, DDL, or DML mutations.

Section 7: Apache Superset Business Intelligence Layer.
Gold analytical data is exposed visually through Apache Superset. Business intelligence is provisioned programmatically using Python REST API scripts, establishing 1 database connection, 7 SqlaTable datasets, 9 slice charts, and 7 published dashboards on Docker port 8088. Executives can inspect clean, interactive pie and table visualizations across Executive Command, Fraud Intelligence, and Retail Demand dashboards without visualization errors.

Section 8: React Command Center Web Application.
For live operational monitoring, the React TypeScript Command Center provides an interactive web interface running on port 3000. Users can type natural language queries into the AI Copilot, view real-time streaming telemetry, monitor sector key performance indicators, and trigger lakehouse runs directly from the browser.

Section 9: Master CI/CD Pipeline and Testing.
DevOps automation is enforced by a four-job GitHub Actions workflow executing on every push to main. The master test runner run_tests.py executes 71 automated unit tests in under 260 seconds with 0 failures and 0 errors. The CI pipeline validates Python logic, Vite React frontend compilation, and multi-stage Docker container builds.

Section 10: Infrastructure Boundary and Google Cloud Platform.
To be completely clear and honest about the infrastructure boundary: Google Cloud Platform resources for project enterprise-data-ai-platform are fully declared using Terraform HCL for Cloud Run services, Cloud Storage Medallion buckets, and BigQuery datasets. However, live Cloud Run hosting was not executed because the project currently operates without an active GCP billing setup.

Section 11: Final Summary and Project Classification.
In summary, this platform combines PySpark data engineering, Databricks Delta Lake synchronization, predictive machine learning, multi-tier generative AI security, native BI dashboards, and continuous integration into one unified architecture. The project is officially classified as an Enterprise-Grade Production-Like Prototype and Release Candidate with 71 passing tests and 0.00 percent Databricks variance.
"""

speaker.Speak(story_script)
stream.Close()
print(f"Successfully generated storytelling narration audio: {audio_path} (Size: {os.path.getsize(audio_path)} bytes)")
