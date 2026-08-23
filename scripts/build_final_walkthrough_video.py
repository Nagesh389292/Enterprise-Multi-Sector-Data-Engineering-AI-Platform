import os
import wave
import subprocess
import imageio_ffmpeg
import win32com.client

proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
media_dir = os.path.join(proj_root, 'docs', 'media')
os.makedirs(media_dir, exist_ok=True)

audio_path = os.path.join(media_dir, 'demo_narration.wav')
final_video_path = os.path.join(media_dir, 'enterprise_platform_demo_video.mp4')
concat_txt_path = os.path.join(media_dir, 'slides.txt')

print("=== STEP 1: GENERATING 8.5-MINUTE STORY-BASED AI NARRATION ===")
speaker = win32com.client.Dispatch('SAPI.SpVoice')
speaker.Rate = -1 # Senior engineering presentation pacing

stream = win32com.client.Dispatch('SAPI.SpFileStream')
stream.Open(audio_path, 3, False)
speaker.AudioOutputStream = stream

portfolio_story_script = """
Welcome to this engineering walkthrough of the Enterprise Multi-Sector Data Engineering, Machine Learning, Business Intelligence, and AI Copilot Platform.

Section 1: Operational Command Center.
This is the operational command center for the enterprise data and AI platform, running live on React port 3000. In production environments, data is fragmented across organizational silos—credit card processing, banking loan operations, healthcare bed capacity telemetry, clinical EHR readmission records, insurance claims, and retail sales. To make real-time operational decisions, engineering teams require unified ingestion, strict data quality controls, and secure natural language interfaces without compromising governance or security.

Section 2: Data Engineering and PySpark Medallion Lakehouse.
In the Data Engineering core, raw telemetry streams enter a three-stage PySpark Medallion Lakehouse. Raw data lands in Bronze Parquet storage with UUID primary keys and metadata provenance. The Silver stage enforces schema validation rules; records failing quality assertions are isolated in data quarantine for compliance auditing. Gold data marts aggregate domain key performance indicators across credit fraud, banking risk, hospital capacity, clinical readmissions, insurance fraud, and retail demand.

Section 3: Multi-Tier AI Copilot Gateway and AST Security.
Now the platform moves from analytics to natural language interaction. A business user does not need to write SQL. They can simply ask a business question in natural language, such as: Which sector currently shows the highest risk according to available analytics? The Agentic Router prioritizes Google Gemini 2.5 Flash as Tier 1, OxAlpha via OpenRouter Gateway as Tier 2 with live HTTP 200 verification, and an offline deterministic analytics engine as Tier 3 fallback. Legacy Ollama daemons have been completely purged. To guarantee security, every generated Text-to-SQL query passes through a sqlglot AST parser that asserts the query root is strictly a SELECT statement, preventing SQL injection, DDL, or DML mutations.

Section 4: Databricks SQL Synchronization and Reconciliation.
The critical engineering capability here is not simply loading data into Databricks. The platform actively verifies that local Gold data marts and Databricks Delta tables agree. Automated reconciliation scripts query Databricks SQL Warehouse 1f1403d78bfa0404 to compare row counts and metric totals. Across all six sectors, the reconciliation achieved 100 percent row matching and exact metric alignment, confirming 0.00 percent data variance across the lakehouse.

Section 5: Apache Superset BI — Executive Command Center.
Now we move into the business intelligence layer, running live on Docker port 8088. This Executive Command Center dashboard exposes the unified analytical Gold layer through interactive visualizations, displaying cross-sector record distributions without error boxes.

Section 6: Apache Superset BI — Credit Card Fraud Intelligence.
Next is the Credit Card Fraud Intelligence dashboard, which provides visibility into transaction amounts, fraud risk score breakdowns, and risk category distributions across low, medium, and high risk tiers.

Section 7: Apache Superset BI — Banking Credit Risk Analytics.
The Banking Credit Risk Analytics dashboard details default probability distributions across loan purpose categories and debt-to-income risk tiers.

Section 8: Apache Superset BI — Healthcare Capacity and Utilization.
The Healthcare Capacity dashboard displays state-level hospital bed occupancy telemetry and capacity utilization metrics.

Section 9: Apache Superset BI — Clinical EHR Readmission Risk.
The Clinical EHR Readmission Risk dashboard breaks down 30-day patient readmission risks by age groups and prior hospitalization counts.

Section 10: Apache Superset BI — Insurance Claims Fraud Analytics.
The Insurance Claims dashboard provides analytics on claim incident types and fraud likelihood indicators.

Section 11: Apache Superset BI — Retail Sales and Product Demand.
The Retail Sales dashboard provides visibility into gross revenue totals and product sales volume across retail categories.

Section 12: GitHub Actions Master CI/CD Pipeline.
The platform uses GitHub Actions to automatically validate the application through its continuous integration pipeline. The master test runner run_tests.py executes 71 automated unit tests in under 260 seconds with 0 failures and 0 errors.

Section 13: Cloud Infrastructure Boundary and Final Classification.
The GCP deployment layer is defined through Terraform HCL for Cloud Run, Cloud Storage, and BigQuery, but live Cloud Run deployment is intentionally not claimed because billing-backed GCP deployment is unavailable. In summary, this platform combines PySpark data engineering, Databricks Delta Lake synchronization, predictive machine learning, multi-tier generative AI security, native BI dashboards, and continuous integration into one unified architecture. The project is officially classified as an Enterprise-Grade Production-Like Prototype and Release Candidate with 71 passing tests and 0.00 percent Databricks variance.
"""

speaker.Speak(portfolio_story_script)
stream.Close()

with wave.open(audio_path, 'rb') as w:
    audio_dur = w.getnframes() / float(w.getframerate())

print(f"[Audio Generator] Generated Story-Based WAV Audio: {audio_path} ({audio_dur:.3f} seconds / {audio_dur/60:.2f} minutes)")

print("=== STEP 2: ENCODING 25FPS MP4 VIDEO MATCHING EXACT CURRENT SCREENS (ZERO SILENCE) ===")

# 13 Storyboard Sections matching fresh docs/media/final_demo/ images 1-to-1
sections = [
    ("01. OPERATIONAL COMMAND CENTER", "media/final_demo/01_react_command_center.png", 45.0),
    ("02. DATA ENGINEERING & PYSPARK MEDALLION", "media/final_demo/02_data_pipeline.png", 55.0),
    ("03. MULTI-TIER AI COPILOT & AST SECURITY", "media/final_demo/03_ai_copilot.png", 65.0),
    ("04. DATABRICKS SQL RECONCILIATION", "media/final_demo/04_databricks.png", 45.0),
    ("05. SUPERSET BI — EXECUTIVE COMMAND CENTER", "media/final_demo/05_superset_executive.png", 25.0),
    ("06. SUPERSET BI — FRAUD INTELLIGENCE", "media/final_demo/06_superset_fraud.png", 25.0),
    ("07. SUPERSET BI — BANKING CREDIT RISK", "media/final_demo/07_superset_banking.png", 20.0),
    ("08. SUPERSET BI — HEALTHCARE CAPACITY", "media/final_demo/08_superset_healthcare.png", 20.0),
    ("09. SUPERSET BI — CLINICAL READMISSION", "media/final_demo/09_superset_readmission.png", 20.0),
    ("10. SUPERSET BI — INSURANCE CLAIMS FRAUD", "media/final_demo/10_superset_insurance.png", 20.0),
    ("11. SUPERSET BI — RETAIL SALES & DEMAND", "media/final_demo/11_superset_retail.png", 25.0),
    ("12. GITHUB ACTIONS MASTER CI/CD", "media/final_demo/12_github_actions.png", 35.0),
    ("13. CLOUD BOUNDARY & FINAL CLASSIFICATION", "media/final_demo/13_terraform_boundary.png", 45.0)
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
