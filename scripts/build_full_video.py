import os
import cv2
import wave
import subprocess
import numpy as np
from PIL import Image, ImageDraw
import imageio_ffmpeg

base_dir = os.path.abspath(os.path.dirname(__file__))
proj_root = os.path.abspath(os.path.join(base_dir, '..'))

audio_path = os.path.join(proj_root, 'docs', 'media', 'demo_narration.wav')
temp_video_path = os.path.join(proj_root, 'docs', 'media', 'temp_no_audio.mp4')
final_video_path = os.path.join(proj_root, 'docs', 'media', 'enterprise_platform_demo_video.mp4')

# 1. Inspect Audio Duration
with wave.open(audio_path, 'rb') as w:
    total_audio_sec = w.getnframes() / float(w.getframerate())

print(f"[Video Builder] Audio Duration: {total_audio_sec:.2f} seconds ({total_audio_sec/60:.2f} minutes)")

# 2. Define Storyboard Sections & Slide Mappings
sections = [
    ("01. INTRODUCTION & BUSINESS CONTEXT", "architecture/platform_architecture_diagram.png", 25.0),
    ("02. END-TO-END SYSTEM TOPOLOGY", "architecture/platform_architecture_diagram.png", 45.0),
    ("03. PYSPARK MEDALLION LAKEHOUSE (BRONZE -> SILVER -> GOLD)", "cicd/master_tests_71_pass.png", 55.0),
    ("04. DATABRICKS DELTA LAKE 6/6 SECTOR RECONCILIATION", "databricks/reconciliation_report.png", 42.0),
    ("05. MLOPS & PREDICTIVE RISK SUITE", "ai/llm_gateway_architecture.png", 42.0),
    ("06. MULTI-TIER AI COPILOT & AST SQL SECURITY", "ai/llm_gateway_architecture.png", 55.0),
    ("07. APACHE SUPERSET BI DASHBOARDS", "dashboards/superset_executive_logged_in.png", 45.0),
    ("08. REACT COMMAND CENTER WEB APPLICATION", "frontend/react_command_center_ui.png", 35.0),
    ("09. MASTER CI/CD PIPELINE & TESTING (71/71 PASS)", "cicd/master_tests_71_pass.png", 32.0),
    ("10. GOOGLE CLOUD PLATFORM TERRAFORM BOUNDARY", "gcp/gcp_console_project.png", 25.0),
    ("11. SUMMARY & OFFICIAL ARCHITECTURE CLASSIFICATION", "architecture/platform_architecture_diagram.png", 20.0)
]

# Scale durations to sum up to total_audio_sec
sum_dur = sum(s[2] for s in sections)
sections = [(s[0], s[1], s[2] * (total_audio_sec / sum_dur)) for s in sections]

width, height = 1280, 720
fps = 10  # 10 fps for ultra-fast rendering while remaining smooth
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))

base_img_dir = os.path.join(proj_root, 'docs', 'images')
total_frames = int(total_audio_sec * fps)
current_frame = 0

print(f"[Video Builder] Fast Rendering ({total_frames} frames at {fps} fps)...")

# Pre-render static frames for each section
for sec_idx, (sec_title, rel_img, sec_dur) in enumerate(sections):
    sec_frames = int(sec_dur * fps)
    img_path = os.path.join(base_img_dir, rel_img)
    
    if os.path.exists(img_path):
        base_img = Image.open(img_path).convert('RGB')
    else:
        base_img = Image.new('RGB', (1120, 560), (30, 41, 59))
        
    # Render keyframe canvas
    canvas = Image.new('RGB', (width, height), (15, 23, 42))
    img_resized = base_img.resize((1120, 560))
    canvas.paste(img_resized, (80, 85))
    
    draw = ImageDraw.Draw(canvas)
    
    # Top Banner Header
    draw.rectangle([0, 0, width, 65], fill=(30, 41, 59))
    draw.text((40, 20), f"ENTERPRISE PLATFORM DEMO | {sec_title}", fill=(56, 189, 248))
    
    # Footer Bar
    draw.rectangle([0, height-55, width, height], fill=(30, 41, 59))
    draw.text((40, height-42), "Status: Release Candidate | Databricks 0.00% Variance | 71/71 Tests PASS | AI Copilot Gemini+OxAlpha", fill=(203, 213, 225))
    
    frame_bgr = cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR)
    
    for f in range(sec_frames):
        current_frame += 1
        out.write(frame_bgr)

out.release()
print(f"[Video Builder] Generated video stream: {temp_video_path} (Size: {os.path.getsize(temp_video_path)} bytes)")

# 3. Mux Audio and Video using FFmpeg
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
print(f"[Video Builder] Muxing audio ({audio_path}) and video using FFmpeg...")

cmd = [
    ffmpeg_exe,
    '-y',
    '-i', temp_video_path,
    '-i', audio_path,
    '-c:v', 'libx264',
    '-preset', 'ultrafast',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-shortest',
    final_video_path
]

res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0:
    print(f"[Video Builder] SUCCESS! Final Muxed MP4: {final_video_path} (Size: {os.path.getsize(final_video_path)} bytes)")
    if os.path.exists(temp_video_path):
        os.remove(temp_video_path)
else:
    print(f"[Video Builder] Muxing warning/error: {res.stderr}")
    # Fallback to copy stream muxing
    cmd_fallback = [
        ffmpeg_exe, '-y', '-i', temp_video_path, '-i', audio_path,
        '-c:v', 'copy', '-c:a', 'aac', '-shortest', final_video_path
    ]
    res2 = subprocess.run(cmd_fallback, capture_output=True, text=True)
    print(f"[Video Builder] Fallback Muxed MP4: {final_video_path} (Size: {os.path.getsize(final_video_path)} bytes)")
    if os.path.exists(temp_video_path):
        os.remove(temp_video_path)
