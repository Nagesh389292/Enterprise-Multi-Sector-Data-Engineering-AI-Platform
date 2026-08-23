import os
import wave
import subprocess
import imageio_ffmpeg

proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
audio_path = os.path.join(proj_root, 'docs', 'media', 'demo_narration.wav')
final_video_path = os.path.join(proj_root, 'docs', 'media', 'enterprise_platform_demo_video.mp4')
concat_txt_path = os.path.join(proj_root, 'docs', 'media', 'slides.txt')

# 1. Inspect Audio Duration
with wave.open(audio_path, 'rb') as w:
    total_audio_sec = w.getnframes() / float(w.getframerate())

print(f"[FFmpeg Fast Builder] Audio Duration: {total_audio_sec:.2f} seconds ({total_audio_sec/60:.2f} minutes)")

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

sum_dur = sum(s[2] for s in sections)
sections = [(s[0], s[1], s[2] * (total_audio_sec / sum_dur)) for s in sections]

base_img_dir = os.path.join(proj_root, 'docs', 'images')

with open(concat_txt_path, 'w') as f:
    for title, rel_img, dur in sections:
        img_path = os.path.join(base_img_dir, rel_img).replace('\\', '/')
        f.write(f"file '{img_path}'\n")
        f.write(f"duration {dur:.2f}\n")
    # Repeat last frame to avoid FFmpeg cut-off
    last_img = os.path.join(base_img_dir, sections[-1][1]).replace('\\', '/')
    f.write(f"file '{last_img}'\n")

print(f"[FFmpeg Fast Builder] Created slide manifest {concat_txt_path}")

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
print(f"[FFmpeg Fast Builder] Executing FFmpeg fast encode & audio mux...")

cmd = [
    ffmpeg_exe,
    '-y',
    '-f', 'concat',
    '-safe', '0',
    '-i', concat_txt_path,
    '-i', audio_path,
    '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p',
    '-c:v', 'libx264',
    '-preset', 'ultrafast',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-shortest',
    final_video_path
]

res = subprocess.run(cmd, capture_output=True, text=True)
print(f"[FFmpeg Fast Builder] Exit code: {res.returncode}")

if os.path.exists(concat_txt_path):
    os.remove(concat_txt_path)

if os.path.exists(final_video_path):
    size_mb = os.path.getsize(final_video_path) / (1024 * 1024)
    print(f"[FFmpeg Fast Builder] SUCCESS! Final Muxed MP4: {final_video_path} ({size_mb:.2f} MB)")
else:
    print(f"[FFmpeg Fast Builder] Error: {res.stderr}")
