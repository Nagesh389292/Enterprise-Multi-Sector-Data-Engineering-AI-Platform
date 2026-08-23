import os
import wave
import subprocess
import imageio_ffmpeg
import win32com.client

proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
media_dir = os.path.join(proj_root, 'docs', 'media')
demo_dir = os.path.join(media_dir, 'final_demo')
os.makedirs(media_dir, exist_ok=True)

audio_path = os.path.join(media_dir, 'demo_narration.wav')
final_video_path = os.path.join(media_dir, 'enterprise_platform_demo_video.mp4')
concat_txt_path = os.path.join(media_dir, 'slides.txt')

print("=== STEP 1: GENERATING 8.5-MINUTE STORYTELLING AI NARRATION ===")
speaker = win32com.client.Dispatch('SAPI.SpVoice')
speaker.Rate = -1 # Senior engineering presentation cadence

stream = win32com.client.Dispatch('SAPI.SpFileStream')
stream.Open(audio_path, 3, False)
speaker.AudioOutputStream = stream

portfolio_story_script = """
Welcome to this engineering walkthrough of the Enterprise Multi-Sector Data Engineering, Machine Learning, Business Intelligence, and AI Copilot Platform.

Section 1: Project and Business Problem.
Why do modern enterprise environments need a multi-sector data engineering and AI platform? In production environments, data is fragmented across organizational silos—credit card processing, banking loan operations, healthcare bed capacity telemetry, clinical EHR readmission records, insurance claims, and retail sales. To make real-time operational decisions, engineering teams require unified ingestion, strict data quality controls, and secure natural language interfaces without compromising governance or security. This platform unifies six distinct industry sectors into a single production-grade lakehouse.

Section 2: End-to-End System Architecture.
Let's trace the complete data journey. External telemetry streams from Alpha Vantage market data, OpenAQ air quality feeds, and economic indicators enter a three-stage PySpark Medallion Lakehouse. Raw data lands in Bronze Parquet storage, is cleaned and schema-validated in Silver with malformed records routed to quarantine, and is aggregated into Gold sector data marts. These Gold marts synchronize to Databricks Delta Lake, PostgreSQL, SQLite, and Apache Superset BI. User natural language queries pass through an Agentic Router to Google Gemini 2.5 Flash, OxAlpha via OpenRouter Gateway, or deterministic fallbacks, guarded by an AST SQL security parser before hitting the analytics engine.

Section 3: Data Engineering and PySpark Medallion Lakehouse.
In the Data Engineering core, raw data enters Bronze storage attached with ingestion timestamps, metadata provenance, and UUID primary keys. The Silver stage enforces schema validation rules; records failing quality assertions are isolated in data quarantine for compliance auditing. Gold data marts summarize domain key performance indicators—credit card fraud scores, banking default risks, hospital bed occupancy rates, clinical readmission risks, insurance fraud probabilities, and retail gross revenue totals.

Section 4: Databricks SQL Synchronization and Reconciliation.
The critical engineering capability here is not simply loading data into Databricks. The platform actively verifies that local Gold data marts and Databricks Delta tables agree. Automated reconciliation scripts query Databricks SQL Warehouse 1f1403d78bfa0404 to compare row counts and metric totals. Across all six sectors, the reconciliation achieved 100 percent row matching and exact metric alignment, confirming 0.00 percent data variance across the lakehouse.

Section 5: Machine Learning and MLOps Suite.
Beyond static analytics, the predictive analytics engine turns this data platform into an intelligence platform. We train multi-sector models across XGBoost, LightGBM, Random Forest, Logistic Regression, and PyTorch Autoencoders. Models are versioned in the MLflow model registry with champion model selection. Explainable AI is powered by SHAP TreeExplainer, revealing the top 3 driver reasons behind every flagged anomaly, while Population Stability Index continuously monitors feature distribution drift over time.

Section 6: Multi-Tier AI Copilot Gateway and AST Security.
Now the platform moves from analytics to natural language interaction. A business user does not need to write SQL. They can simply ask a question in natural language, such as: Which sector currently shows the highest risk according to available analytics? The Agentic Router prioritizes Google Gemini 2.5 Flash as Tier 1, OxAlpha via OpenRouter Gateway as Tier 2 with live HTTP 200 verification, and an offline deterministic analytics engine as Tier 3 fallback. Legacy Ollama daemons have been completely purged. To guarantee security, every generated Text-to-SQL query passes through a sqlglot AST parser that asserts the query root is strictly a SELECT statement, preventing SQL injection, DDL, or DML mutations.

Section 7: Apache Superset Business Intelligence Layer.
Gold analytical data is exposed visually through Apache Superset. Business intelligence is provisioned programmatically using Python REST API scripts, establishing 1 database connection, 7 SqlaTable datasets, 9 slice charts, and 7 published dashboards on Docker port 8088. Executives can inspect clean, interactive pie and table visualizations across Executive Command, Fraud Intelligence, and Retail Demand dashboards without visualization errors.

Section 8: React Command Center Web Application.
For live operational monitoring, the React TypeScript Command Center provides an interactive web interface running on port 3000. Users can type natural language queries into the AI Copilot, view real-time streaming telemetry, monitor sector key performance indicators, and trigger lakehouse runs directly from the browser.

Section 9: Master CI/CD Pipeline and Testing.
DevOps automation is enforced by a four-job GitHub Actions workflow executing on every push to main. The master test runner run_tests.py executes 71 automated unit tests in under 260 seconds with 0 failures and 0 errors. The CI pipeline validates Python logic, Vite React frontend compilation, and multi-stage Docker container builds.

Section 10: Infrastructure Boundary and Google Cloud Platform.
To be completely clear and honest about the infrastructure boundary: Google Cloud Platform resources for project enterprise-data-ai-platform are fully declared using Terraform HCL for Cloud Run services, Cloud Storage Medallion buckets, and BigQuery datasets. However, live Cloud Run hosting was intentionally not executed because the project currently operates without an active GCP billing setup.

Section 11: Final Summary and Project Classification.
In summary, this platform combines PySpark data engineering, Databricks Delta Lake synchronization, predictive machine learning, multi-tier generative AI security, native BI dashboards, and continuous integration into one unified architecture. The project is officially classified as an Enterprise-Grade Production-Like Prototype and Release Candidate with 71 passing tests and 0.00 percent Databricks variance.
"""

speaker.Speak(portfolio_story_script)
stream.Close()

with wave.open(audio_path, 'rb') as w:
    audio_dur = w.getnframes() / float(w.getframerate())

print(f"[Audio Generator] Generated Storytelling WAV Audio: {audio_path} ({audio_dur:.3f} seconds / {audio_dur/60:.2f} minutes)")

print("=== STEP 2: ENCODING 25FPS MP4 VIDEO WITH EMBEDDED AAC AUDIO (ZERO SILENCE) ===")

# 11 Storyboard Sections matching fresh docs/media/final_demo/ images
sections = [
    ("01. PROJECT & BUSINESS PROBLEM", "media/final_demo/01_architecture.png", 45.0),
    ("02. END-TO-END SYSTEM ARCHITECTURE", "media/final_demo/01_architecture.png", 45.0),
    ("03. DATA ENGINEERING & PYSPARK MEDALLION", "media/final_demo/02_data_pipeline.png", 60.0),
    ("04. DATABRICKS SQL RECONCILIATION", "media/final_demo/03_databricks_reconciliation.png", 50.0),
    ("05. MACHINE LEARNING & MLOPS SUITE", "media/final_demo/04_ml_mlops.png", 50.0),
    ("06. AI COPILOT & GATEWAY SECURITY", "media/final_demo/05_ai_copilot.png", 70.0),
    ("07. APACHE SUPERSET BI DASHBOARDS", "media/final_demo/06_superset_executive.png", 70.0),
    ("08. REACT COMMAND CENTER WEB APP", "media/final_demo/09_react_command_center.png", 50.0),
    ("09. GITHUB ACTIONS MASTER CI/CD", "media/final_demo/10_github_actions.png", 40.0),
    ("10. TERRAFORM GCP CLOUD BOUNDARY", "media/final_demo/11_terraform_boundary.png", 40.0),
    ("11. FINAL SUMMARY & CLASSIFICATION", "media/final_demo/01_architecture.png", 30.0)
]

sum_dur = sum(s[2] for s in sections)
sections = [(s[0], s[1], s[2] * (audio_dur / sum_dur)) for s in sections]

base_docs_dir = os.path.join(proj_root, 'docs')

with open(concat_txt_path, 'w') as f:
    for title, rel_img, dur in sections:
        img_path = os.path.join(base_docs_dir, rel_img).replace('\\', '/')
        f.write(f"file '{img_path}'\n")
        f.write(f"duration {dur:.3f}\n")
    # Last entry without duration for FFmpeg concat demuxer requirement
    last_img = os.path.join(base_docs_dir, sections[-1][1]).replace('\\', '/')
    f.write(f"file '{last_img}'\n")

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
print(f"[FFmpeg Encoder] Encoding 25fps H.264 video + AAC audio (Exact Trimmed Duration: {audio_dur:.3f}s)...")

cmd = [
    ffmpeg_exe,
    '-y',
    '-f', 'concat',
    '-safe', '0',
    '-i', concat_txt_path,
    '-i', audio_path,
    '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p',
    '-r', '25',
    '-c:v', 'libx264',
    '-preset', 'ultrafast',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-t', str(audio_dur),
    final_video_path
]

res = subprocess.run(cmd, capture_output=True, text=True)
print(f"[FFmpeg Encoder] Exit code: {res.returncode}")

if os.path.exists(concat_txt_path):
    os.remove(concat_txt_path)

if os.path.exists(final_video_path):
    size_mb = os.path.getsize(final_video_path) / (1024 * 1024)
    print(f"[FFmpeg Encoder] SUCCESS! Final Muxed MP4: {final_video_path} ({size_mb:.2f} MB)")
else:
    print(f"[FFmpeg Encoder] Error: {res.stderr}")
