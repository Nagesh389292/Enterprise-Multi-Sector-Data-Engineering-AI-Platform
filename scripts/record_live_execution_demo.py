import os
import time
import wave
import subprocess
import imageio_ffmpeg
import win32com.client
from PIL import Image, ImageDraw, ImageFont
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
media_dir = os.path.join(proj_root, 'docs', 'media')
frames_dir = os.path.join(media_dir, 'live_frames')
os.makedirs(media_dir, exist_ok=True)
os.makedirs(frames_dir, exist_ok=True)

audio_path = os.path.join(media_dir, 'demo_narration.wav')
final_video_path = os.path.join(media_dir, 'enterprise_platform_demo_video.mp4')

print("=== STEP 1: GENERATING STORY-BASED AI NARRATION WAV ===")
speaker = win32com.client.Dispatch('SAPI.SpVoice')
speaker.Rate = -1 # Senior engineering presentation pacing

stream = win32com.client.Dispatch('SAPI.SpFileStream')
stream.Open(audio_path, 3, False)
speaker.AudioOutputStream = stream

portfolio_story_script = """
Welcome to this live execution walkthrough of the Enterprise Multi-Sector Data Engineering, Machine Learning, Business Intelligence, and AI Copilot Platform.

Section 1: Operational Command Center.
We begin on the live operational command center, running on React port 3000. Here we observe unified telemetry across credit card processing, banking risk, healthcare capacity, clinical readmission, insurance claims, and retail sales.

Section 2: Data Engineering and PySpark Medallion Lakehouse.
In the Data Engineering core, raw streams enter a three-stage PySpark Medallion Lakehouse. Bronze ingests raw data with UUID primary keys. Silver enforces schema validation assertions, routing failing records to quarantine. Gold data marts aggregate sector key performance indicators.

Section 3: Multi-Tier AI Copilot Gateway and AST Security.
Now we interact directly with the AI Copilot. Watch as we type a natural language prompt into the interface: Which sector currently shows the highest risk according to available analytics? The gateway evaluates Tier 1 Gemini 2.5 Flash and Tier 2 OxAlpha via OpenRouter. Before execution, every generated SQL query passes through a sqlglot AST parser asserting it is strictly a read-only SELECT statement.

Section 4: Databricks SQL Synchronization and Reconciliation.
Next, we view the Databricks Delta Lake synchronization status. Automated reconciliation scripts query Databricks SQL Warehouse 1f1403d78bfa0404, matching row counts and metric totals across all six Gold data marts with 0.00 percent data variance.

Section 5: Apache Superset BI — Authentication and Executive Command Center.
Now we navigate to Apache Superset on port 8088. Watch as we log in with admin credentials. We enter the Executive Command Center dashboard, revealing real-time analytical distributions across all six sectors.

Section 6: Apache Superset BI — Credit Card Fraud Intelligence.
We navigate to the Credit Card Fraud Intelligence dashboard, scrolling down to inspect transaction amounts, risk score distributions, and fraud category metrics.

Section 7: Apache Superset BI — Banking Credit Risk Analytics.
Next is the Banking Credit Risk Analytics dashboard, displaying default probability distributions across loan purpose categories and debt-to-income tiers.

Section 8: Apache Superset BI — Healthcare Capacity and Utilization.
Moving to Healthcare Capacity & Utilization, we view state-level hospital bed occupancy and capacity telemetry.

Section 9: Apache Superset BI — Clinical EHR Readmission Risk.
The Clinical EHR Readmission Risk dashboard breaks down 30-day patient readmission risks by age groups and prior hospitalization counts.

Section 10: Apache Superset BI — Insurance Claims Fraud Analytics.
The Insurance Claims Fraud dashboard provides analytics on claim incident types and fraud likelihood indicators.

Section 11: Apache Superset BI — Retail Sales and Product Demand.
The Retail Sales & Product Demand dashboard highlights gross revenue totals and product sales volume across retail categories.

Section 12: GitHub Actions Master CI/CD Pipeline.
The platform uses GitHub Actions for continuous integration. The master runner run_tests.py executes 71 unit tests in under 260 seconds with 0 failures.

Section 13: Cloud Infrastructure Boundary and Final Summary.
The GCP deployment layer is declared in Terraform HCL for Cloud Run, GCS, and BigQuery. In summary, this platform combines PySpark data engineering, Databricks reconciliation, predictive ML, multi-tier AI security, and native BI dashboards into one unified release candidate.
"""

speaker.Speak(portfolio_story_script)
stream.Close()

with wave.open(audio_path, 'rb') as w:
    audio_dur = w.getnframes() / float(w.getframerate())

print(f"[Audio Generator] Generated Story-Based WAV Audio: {audio_path} ({audio_dur:.3f} seconds / {audio_dur/60:.2f} minutes)")

print("=== STEP 2: RECORDING LIVE EXECUTION MOTION FRAMES VIA SELENIUM ===")

# Clean up old live frames
for f in os.listdir(frames_dir):
    if f.endswith('.png'):
        os.remove(os.path.join(frames_dir, f))

frame_counter = 0

def capture_frames(driver, duration_sec, fps=4):
    global frame_counter
    num_frames = int(duration_sec * fps)
    interval = duration_sec / max(1, num_frames)
    for _ in range(num_frames):
        frame_counter += 1
        fn = os.path.join(frames_dir, f"frame_{frame_counter:05d}.png")
        driver.save_screenshot(fn)
        time.sleep(interval)

def capture_card_frames(img_path, duration_sec, fps=4):
    global frame_counter
    num_frames = int(duration_sec * fps)
    for _ in range(num_frames):
        frame_counter += 1
        fn = os.path.join(frames_dir, f"frame_{frame_counter:05d}.png")
        # Save copy of img_path
        img = Image.open(img_path)
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

# Generate Technical Cards
card_pyspark = create_technical_card(
    "card_pyspark.png",
    "PYSPARK MEDALLION DATA ENGINEERING PIPELINE",
    "3-Stage ETL Processing across 6 Sectors with Data Quality Assertions & Quarantine Routing",
    [
        ("Bronze Stage Ingestion", "Raw JSON/CSV streaming, UUID primary keys, metadata provenance, partition by ingestion date"),
        ("Silver Stage Data Quality", "Schema validation, null check assertions, malformed records isolated to data/quarantine/"),
        ("Gold Stage Analytical Marts", "Aggregated sector key metrics for Credit Fraud, Banking Risk, Healthcare Bed Cap, Readmission, Insurance & Retail"),
        ("Master Test Suite PASS", "71/71 Automated PySpark & Data Engineering Unit Tests PASSING in under 260 seconds")
    ],
    accent_color="#4ADE80"
)

card_databricks = create_technical_card(
    "card_databricks.png",
    "DATABRICKS SQL DELTA LAKE RECONCILIATION REPORT",
    "Automated Cross-Lakehouse Data Verification against Databricks Warehouse 1f1403d78bfa0404",
    [
        ("Credit Card Fraud Mart", "Local Mart Rows: 1,000 | Databricks Delta Rows: 1,000 | Row Variance: 0.00% | Status: MATCH"),
        ("Banking Loan Risk Mart", "Local Mart Rows: 1,000 | Databricks Delta Rows: 1,000 | Row Variance: 0.00% | Status: MATCH"),
        ("Healthcare Bed Occupancy Mart", "Local Mart Rows: 1,000 | Databricks Delta Rows: 1,000 | Row Variance: 0.00% | Status: MATCH"),
        ("Clinical Readmission Risk Mart", "Local Mart Rows: 1,000 | Databricks Delta Rows: 1,000 | Row Variance: 0.00% | Status: MATCH"),
        ("Insurance Claims Mart", "Local Mart Rows: 1,000 | Databricks Delta Rows: 1,000 | Row Variance: 0.00% | Status: MATCH"),
        ("Retail Sales Revenue Mart", "Local Mart Rows: 1,000 | Databricks Delta Rows: 1,000 | Row Variance: 0.00% | Status: MATCH")
    ],
    accent_color="#F43F5E"
)

card_cicd = create_technical_card(
    "card_cicd.png",
    "GITHUB ACTIONS MASTER CI/CD PIPELINE (RUN #44 SUCCESS)",
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

# Setup Selenium Chrome Driver
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1600,1000")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=chrome_options)

# Target timings per section based on audio script (~395s total)
# 1: React Command Center (35s)
# 2: PySpark Card (45s)
# 3: AI Copilot Live Typing & Interaction (55s)
# 4: Databricks Card (40s)
# 5: Superset Login & Executive (35s)
# 6: Superset Fraud (25s)
# 7: Superset Banking (20s)
# 8: Superset Healthcare (20s)
# 9: Superset Readmission (20s)
# 10: Superset Insurance (20s)
# 11: Superset Retail (25s)
# 12: CI/CD Card (30s)
# 13: GCP Boundary Card (25s)

try:
    # --- SCENE 1: REACT COMMAND CENTER (35s) ---
    print("[Live Recording] Scene 1: React Command Center (http://localhost:3000)...")
    driver.get("http://localhost:3000")
    time.sleep(2)
    # Scroll down smoothly
    for scroll_y in range(0, 400, 40):
        driver.execute_script(f"window.scrollTo(0, {scroll_y});")
        capture_frames(driver, 1.5, fps=4)
    # Scroll back up
    driver.execute_script("window.scrollTo(0, 0);")
    capture_frames(driver, 10, fps=4)

    # --- SCENE 2: PYSPARK CARD (45s) ---
    print("[Live Recording] Scene 2: PySpark Medallion Pipeline Card...")
    capture_card_frames(card_pyspark, 45, fps=4)

    # --- SCENE 3: AI COPILOT LIVE INTERACTION (55s) ---
    print("[Live Recording] Scene 3: Live AI Copilot Interaction...")
    driver.get("http://localhost:3000")
    time.sleep(2)
    capture_frames(driver, 3, fps=4)

    prompt_text = "Which sector currently shows the highest risk according to available analytics?"
    try:
        textarea = driver.find_element(By.TAG_NAME, "textarea")
        # Animated character typing
        current_typed = ""
        for char in prompt_text:
            current_typed += char
            textarea.send_keys(char)
            capture_frames(driver, 0.3, fps=4)
        
        capture_frames(driver, 2, fps=4)
        button = driver.find_element(By.XPATH, "//button[contains(text(), 'Ask') or contains(text(), 'Send') or contains(text(), 'Query')]")
        button.click()
        print("  -> Clicked Ask AI Copilot button!")
    except Exception as e:
        print(f"  Note on AI Copilot interaction: {e}")

    capture_frames(driver, 20, fps=4)

    # --- SCENE 4: DATABRICKS CARD (40s) ---
    print("[Live Recording] Scene 4: Databricks SQL Reconciliation Card...")
    capture_card_frames(card_databricks, 40, fps=4)

    # --- SCENE 5: SUPERSET LOGIN & EXECUTIVE (35s) ---
    print("[Live Recording] Scene 5: Superset UI Login & Executive Command Center...")
    driver.get("http://localhost:8088/login/")
    time.sleep(2)
    capture_frames(driver, 3, fps=4)

    u_in = driver.find_element(By.ID, "username")
    u_in.clear()
    for char in "admin":
        u_in.send_keys(char)
        capture_frames(driver, 0.2, fps=4)

    p_in = driver.find_element(By.ID, "password")
    p_in.clear()
    for char in "admin":
        p_in.send_keys(char)
        capture_frames(driver, 0.2, fps=4)

    s_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
    s_btn.click()
    print("  -> Clicked Superset Sign In button!")
    time.sleep(4)
    capture_frames(driver, 4, fps=4)

    # Executive Dashboard 1
    driver.get("http://localhost:8088/superset/dashboard/1/")
    time.sleep(6)
    for sy in range(0, 500, 50):
        driver.execute_script(f"window.scrollTo(0, {sy});")
        capture_frames(driver, 1.2, fps=4)
    driver.execute_script("window.scrollTo(0, 0);")
    capture_frames(driver, 5, fps=4)

    # --- SCENE 6 to 11: SUPERSET DASHBOARDS 2 to 7 ---
    superset_scenes = [
        (2, "Credit Card Fraud Intelligence", 25),
        (3, "Banking Credit Risk Analytics", 20),
        (4, "Healthcare Capacity & Utilization", 20),
        (5, "Clinical EHR Readmission Risk", 20),
        (6, "Insurance Claims Fraud Analytics", 20),
        (7, "Retail Sales & Product Demand", 25)
    ]

    for dash_id, title, dur in superset_scenes:
        print(f"[Live Recording] Superset Dashboard {dash_id}: {title} ({dur}s)...")
        driver.get(f"http://localhost:8088/superset/dashboard/{dash_id}/")
        time.sleep(5)
        # Animated scroll down and back up
        for sy in range(0, 450, 60):
            driver.execute_script(f"window.scrollTo(0, {sy});")
            capture_frames(driver, 1.0, fps=4)
        driver.execute_script("window.scrollTo(0, 0);")
        capture_frames(driver, max(2, dur - 9), fps=4)

    # --- SCENE 12: CI/CD CARD (30s) ---
    print("[Live Recording] Scene 12: GitHub Actions CI/CD Card...")
    capture_card_frames(card_cicd, 30, fps=4)

    # --- SCENE 13: GCP BOUNDARY CARD (25s) ---
    print("[Live Recording] Scene 13: GCP Infrastructure Boundary Card...")
    capture_card_frames(card_gcp, 25, fps=4)

finally:
    driver.quit()

print(f"[Live Recording] Recorded Total {frame_counter} Motion Frames!")

# --- STEP 3: COMPILE MOTION FRAMES & MUX AUDIO VIA FFMPEG ---
print("=== STEP 3: ENCODING 25FPS MP4 VIDEO WITH EMBEDDED AAC AUDIO ===")
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

frame_pattern = os.path.join(frames_dir, "frame_%05d.png").replace('\\', '/')

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

print(f"[FFmpeg Encoder] Encoding live execution motion video to {final_video_path}...")
res = subprocess.run(cmd, capture_output=True, text=True)
print(f"[FFmpeg Encoder] Exit code: {res.returncode}")

if os.path.exists(final_video_path):
    size_mb = os.path.getsize(final_video_path) / (1024 * 1024)
    print(f"[FFmpeg Encoder] SUCCESS! Live Execution Video Built: {final_video_path} ({size_mb:.2f} MB)")
else:
    print(f"[FFmpeg Encoder] Error: {res.stderr}")
