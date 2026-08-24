import os
import time
import wave
import subprocess
import imageio_ffmpeg
import win32com.client
from PIL import Image, ImageDraw, ImageFont

proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
media_dir = os.path.join(proj_root, 'docs', 'media')
final_demo_dir = os.path.join(media_dir, 'final_demo')
frames_dir = os.path.join(media_dir, 'live_frames')
os.makedirs(media_dir, exist_ok=True)
os.makedirs(frames_dir, exist_ok=True)

audio_path = os.path.join(media_dir, 'demo_narration.wav')
final_video_path = os.path.join(media_dir, 'enterprise_platform_demo_video.mp4')

print("=== STEP 1: GENERATING FIRST-PERSON PRODUCT DEMO NARRATION WAV ===")
speaker = win32com.client.Dispatch('SAPI.SpVoice')
speaker.Rate = -1 # Senior engineering presentation pacing

stream = win32com.client.Dispatch('SAPI.SpFileStream')
stream.Open(audio_path, 3, False)
speaker.AudioOutputStream = stream

portfolio_story_script = """
Welcome to this technical demonstration of our Enterprise Multi-Sector Data Engineering, Machine Learning, Business Intelligence, and AI Copilot Platform. Here, we see the live operational command center processing real-time telemetry across financial, healthcare, clinical, insurance, and retail sectors.

Section 1: End-to-End System Architecture.
Here I am demonstrating our master platform architecture. Raw data streams from internal operational databases, Kafka, REST APIs, and public feeds into our PySpark Medallion Lakehouse on Databricks Delta Lake. The analytics layer combines MLOps, an AI Copilot gateway, and Apache Superset BI dashboards.

Section 2: Data Engineering and PySpark Medallion Pipeline.
In the data engineering layer, raw streams are ingested into the Bronze stage with UUID primary keys. The Silver stage enforces schema validation assertions and null checks, isolating malformed records into quarantine. The Gold layer creates curated data marts for cross-sector business analytics.

Section 3: Databricks SQL 6/6 Reconciliation.
Here I am demonstrating the Databricks layer, where curated Gold data is reconciled against our live Databricks SQL warehouse. Automated reconciliation scripts check row counts and metric totals across all six sector data marts, confirming zero percent metric variance.

Section 4: Multi-Tier AI Copilot Gateway and AST Security.
The AI Copilot provides a natural language interface over the platform. The LLM gateway uses Gemini 2.5 Flash as the primary model and OxAlpha via OpenRouter as the secondary provider. Before execution, every generated SQL query passes through a sqlglot AST parser asserting it is strictly a read-only SELECT statement.

Section 5: Apache Superset BI — Executive Command Center.
The curated Gold data is exposed through Apache Superset. Here we see the Executive Command Center dashboard, displaying real-time analytical distributions across all six sectors.

Section 6: Apache Superset BI — Financial and Healthcare Sector Dashboards.
Here we examine the sector-specific BI dashboards. The Credit Card Fraud dashboard tracks transaction risk scores, Banking Credit Risk analyzes default probabilities by loan category, and Healthcare Utilization tracks state-level bed occupancy.

Section 7: Apache Superset BI — Clinical, Insurance and Retail Dashboards.
Continuing through the BI layer, Clinical EHR Readmission tracks thirty-day patient risk, Insurance Claims analyzes fraud indicators by incident type, and Retail Sales displays gross revenue and product demand.

Section 8: React Operational Command Center Detailed View.
Returning to the React command center, users can interactively inspect sector telemetry, trigger analytical pipelines, and monitor platform health in real time.

Section 9: GitHub Actions Master CI/CD and Automated Testing.
The platform enforces automated quality control through GitHub Actions. Our master test suite executes 71 automated unit tests covering PySpark pipelines, Databricks reconciliation, ML models, and security rules with 100 percent pass rate.

Section 10: Cloud Infrastructure Boundary and Final Platform Summary.
Finally, our cloud infrastructure is declared in Terraform HCL for GCP Cloud Run, Cloud Storage, and BigQuery. In summary, this platform combines enterprise data engineering, Databricks reconciliation, MLOps, AI security, and native BI into a production-like release candidate.
"""

speaker.Speak(portfolio_story_script)
stream.Close()

with wave.open(audio_path, 'rb') as w:
    audio_dur = w.getnframes() / float(w.getframerate())

print(f"[Audio Generator] Generated Story-Based WAV Audio: {audio_path} ({audio_dur:.3f} seconds / {audio_dur/60:.2f} minutes)")

print("=== STEP 2: PREPARING HIGH-RESOLUTION SCENE CARDS & FRAMES ===")

# Clean up old live frames
for f in os.listdir(frames_dir):
    if f.endswith('.png'):
        try:
            os.remove(os.path.join(frames_dir, f))
        except Exception:
            pass

frame_counter = 0

def prepare_framed_image(img_path, output_name, bg_color="#0F172A"):
    img = Image.open(img_path)
    w, h = 1600, 1000
    card = Image.new("RGB", (w, h), bg_color)
    img_resized = img.copy()
    img_resized.thumbnail((1560, 960), Image.Resampling.LANCZOS)
    offset_x = (w - img_resized.width) // 2
    offset_y = (h - img_resized.height) // 2
    card.paste(img_resized, (offset_x, offset_y))
    out_p = os.path.join(media_dir, output_name)
    card.save(out_p)
    return out_p

def capture_card_frames(img_path, duration_sec, fps=4):
    global frame_counter
    num_frames = int(duration_sec * fps)
    img_framed_path = prepare_framed_image(img_path, "temp_frame.png")
    img = Image.open(img_framed_path)
    for _ in range(num_frames):
        frame_counter += 1
        fn = os.path.join(frames_dir, f"frame_{frame_counter:05d}.png")
        img.save(fn)

def create_technical_card(filename, title, subtitle, items, bg_color="#0F172A", accent_color="#38BDF8"):
    w, h = 1600, 1000
    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arial.ttf", 36)
        sub_font = ImageFont.truetype("arial.ttf", 22)
        body_font = ImageFont.truetype("arial.ttf", 19)
    except Exception:
        title_font = sub_font = body_font = ImageFont.load_default()

    draw.rectangle([40, 40, w - 40, 140], fill="#1E293B", outline=accent_color, width=2)
    draw.text((70, 60), title, fill="#F8FAFC", font=title_font)
    draw.text((70, 105), subtitle, fill=accent_color, font=sub_font)

    y = 175
    for label, detail in items:
        draw.rectangle([40, y, w - 40, y + 105], fill="#1E293B", outline="#334155", width=1)
        draw.rectangle([40, y, 50, y + 105], fill=accent_color)
        draw.text((70, y + 20), label, fill="#F8FAFC", font=sub_font)
        draw.text((70, y + 55), detail, fill="#94A3B8", font=body_font)
        y += 120

    draw.rectangle([0, h - 45, w, h], fill="#0284C7")
    draw.text((40, h - 32), "ENTERPRISE MULTI-SECTOR DATA ENGINEERING & AI PLATFORM — RELEASE CANDIDATE", fill="#FFFFFF", font=body_font)

    out_p = os.path.join(media_dir, filename)
    img.save(out_p)
    return out_p

# Generate Technical Cards for CI/CD and GCP
card_cicd = create_technical_card(
    "card_cicd.png",
    "GITHUB ACTIONS MASTER CI/CD PIPELINE (RUN #55 SUCCESS)",
    "Continuous Integration & Automated Build Verification on Every Push to Main Branch",
    [
        ("Job 1: test-python", "Executes 71/71 Master Unit Tests across PySpark, Databricks, ML, and AI Copilot (Status: SUCCESS)"),
        ("Job 2: build-frontend", "Compiles production React TypeScript single-page app bundle using Vite (Status: SUCCESS)"),
        ("Job 3: docker-build", "Builds multi-stage backend and frontend Docker container images (Status: SUCCESS)"),
        ("Job 4: deploy-gcp-cloud-run", "Validates GCP Cloud Run credentials & Terraform HCL manifests (Status: SUCCESS)")
    ],
    accent_color="#22C55E"
)

card_gcp = create_technical_card(
    "card_gcp.png",
    "CLOUD INFRASTRUCTURE BOUNDARY — TERRAFORM HCL DECLARED",
    "Honest GCP Architecture Boundary: IaC Defined for Cloud Run, Cloud Storage & BigQuery",
    [
        ("GCP Project ID", "enterprise-data-ai-platform (Project Number: 902040617953)"),
        ("Terraform HCL Manifests", "infrastructure/terraform/main.tf (Cloud Run, GCS Medallion Buckets, BigQuery Datasets)"),
        ("Deployment Classification", "Release Candidate / Production-Like Prototype — Live Cloud Run hosting is intentionally unexecuted to maintain a 0-cost local baseline")
    ],
    accent_color="#EAB308"
)

arch_diagram_path = os.path.join(media_dir, 'architecture_diagram.png')
if not os.path.exists(arch_diagram_path):
    arch_diagram_path = os.path.join(proj_root, 'docs', 'images', 'architecture_diagram.png')

# Scene Flow mapped precisely to narration sections (~390s total)
scene_sources = [
    ("Scene 1: Platform Overview & Intro", os.path.join(final_demo_dir, "01_react_command_center.png"), 30),
    ("Scene 2: End-to-End System Architecture", arch_diagram_path, 45),
    ("Scene 3: PySpark Data Engineering Pipeline", os.path.join(final_demo_dir, "02_data_pipeline.png"), 45),
    ("Scene 4: Databricks SQL 6/6 Reconciliation", os.path.join(final_demo_dir, "04_databricks.png"), 45),
    ("Scene 5: Multi-Tier AI Copilot & AST Security", os.path.join(final_demo_dir, "03_ai_copilot.png"), 45),
    ("Scene 6: Superset BI Executive Command Center", os.path.join(final_demo_dir, "05_superset_executive.png"), 30),
    ("Scene 7: Superset Credit Card Fraud Intelligence", os.path.join(final_demo_dir, "06_superset_fraud.png"), 20),
    ("Scene 8: Superset Banking Credit Risk Analytics", os.path.join(final_demo_dir, "07_superset_banking.png"), 20),
    ("Scene 9: Superset Healthcare Capacity & Utilization", os.path.join(final_demo_dir, "08_superset_healthcare.png"), 20),
    ("Scene 10: Superset Clinical EHR Readmission Risk", os.path.join(final_demo_dir, "09_superset_readmission.png"), 20),
    ("Scene 11: Superset Insurance Claims Fraud Analytics", os.path.join(final_demo_dir, "10_superset_insurance.png"), 20),
    ("Scene 12: Superset Retail Sales & Product Demand", os.path.join(final_demo_dir, "11_superset_retail.png"), 20),
    ("Scene 13: React Command Center Detailed View", os.path.join(final_demo_dir, "01_react_command_center.png"), 30),
    ("Scene 14: GitHub Actions Master CI/CD Pipeline", card_cicd, 30),
    ("Scene 15: Cloud Infrastructure Boundary", card_gcp, 30)
]

for title, path, dur in scene_sources:
    print(f"[Frame Recorder] {title} ({dur}s)...")
    capture_card_frames(path, dur, fps=4)

print(f"[Frame Recorder] Recorded Total {frame_counter} High-Resolution Motion Frames!")

# --- STEP 3: COMPILE MOTION FRAMES & MUX AUDIO VIA FFMPEG ---
print("=== STEP 3: ENCODING 25FPS MP4 VIDEO WITH EMBEDDED AAC AUDIO ===")
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

cmd = [
    ffmpeg_exe,
    '-y',
    '-framerate', '4', # 4 motion frames captured per second
    '-i', os.path.join(frames_dir, 'frame_%05d.png'),
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

print(f"[FFmpeg Encoder] Encoding demonstration video to {final_video_path}...")
res = subprocess.run(cmd, capture_output=True, text=True)
print(f"[FFmpeg Encoder] Exit code: {res.returncode}")

if os.path.exists(final_video_path):
    size_mb = os.path.getsize(final_video_path) / (1024 * 1024)
    print(f"[FFmpeg Encoder] SUCCESS! Video Built: {final_video_path} ({size_mb:.2f} MB)")
else:
    print(f"[FFmpeg Encoder] Error: {res.stderr}")
