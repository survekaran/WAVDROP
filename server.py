import os
import uuid
import threading
import time
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Track jobs: {job_id: {status, progress, filename, error}}
jobs = {}

def cleanup_old_files():
    """Remove files older than 30 minutes."""
    while True:
        now = time.time()
        for folder in [UPLOAD_DIR, OUTPUT_DIR]:
            for f in os.listdir(folder):
                fp = os.path.join(folder, f)
                if os.path.isfile(fp) and now - os.path.getmtime(fp) > 1800:
                    os.remove(fp)
        time.sleep(300)

threading.Thread(target=cleanup_old_files, daemon=True).start()


def convert_youtube(url, job_id, quality):
    jobs[job_id] = {"status": "downloading", "progress": 0, "filename": None, "error": None}
    output_template = os.path.join(OUTPUT_DIR, f"{job_id}.%(ext)s")

    def progress_hook(d):
        if d["status"] == "downloading":
            pct = d.get("_percent_str", "0%").strip().replace("%", "")
            try:
                jobs[job_id]["progress"] = min(int(float(pct)), 95)
            except:
                pass
        elif d["status"] == "finished":
            jobs[job_id]["status"] = "converting"
            jobs[job_id]["progress"] = 97

    audio_quality = {"high": "0", "medium": "5", "low": "9"}.get(quality, "0")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "progress_hooks": [progress_hook],
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": audio_quality,
        }],
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "audio")
            safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()[:60]
            mp3_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp3")
            if os.path.exists(mp3_path):
                jobs[job_id]["status"] = "done"
                jobs[job_id]["progress"] = 100
                jobs[job_id]["filename"] = f"{safe_title}.mp3"
                jobs[job_id]["file_id"] = job_id
            else:
                jobs[job_id]["status"] = "error"
                jobs[job_id]["error"] = "MP3 file not created"
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)


def convert_upload(filepath, job_id, quality):
    jobs[job_id] = {"status": "converting", "progress": 50, "filename": None, "error": None}
    output_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp3")
    audio_quality = {"high": "0", "medium": "5", "low": "9"}.get(quality, "0")

    import subprocess
    try:
        bitrate = {"high": "320k", "medium": "192k", "low": "128k"}.get(quality, "320k")
        result = subprocess.run(
            ["ffmpeg", "-i", filepath, "-vn", "-ab", bitrate, "-ar", "44100", "-y", output_path],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            original_name = os.path.splitext(os.path.basename(filepath))[0]
            jobs[job_id]["status"] = "done"
            jobs[job_id]["progress"] = 100
            jobs[job_id]["filename"] = f"{original_name}.mp3"
            jobs[job_id]["file_id"] = job_id
        else:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = result.stderr[-200:] if result.stderr else "FFmpeg error"
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


@app.route("/api/convert/url", methods=["POST"])
def convert_url():
    data = request.json
    url = data.get("url", "").strip()
    quality = data.get("quality", "high")
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    job_id = str(uuid.uuid4())
    thread = threading.Thread(target=convert_youtube, args=(url, job_id, quality))
    thread.daemon = True
    thread.start()
    return jsonify({"job_id": job_id})


@app.route("/api/convert/file", methods=["POST"])
def convert_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    quality = request.form.get("quality", "high")
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    allowed = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv", ".m4a", ".ogg", ".wav", ".aac", ".flac"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        return jsonify({"error": f"Unsupported format: {ext}"}), 400

    job_id = str(uuid.uuid4())
    save_path = os.path.join(UPLOAD_DIR, f"{job_id}{ext}")
    file.save(save_path)
    thread = threading.Thread(target=convert_upload, args=(save_path, job_id, quality))
    thread.daemon = True
    thread.start()
    return jsonify({"job_id": job_id})


@app.route("/api/status/<job_id>")
def job_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


@app.route("/api/download/<file_id>")
def download_file(file_id):
    # Sanitize
    file_id = file_id.replace("..", "").replace("/", "")
    mp3_path = os.path.join(OUTPUT_DIR, f"{file_id}.mp3")
    if not os.path.exists(mp3_path):
        return jsonify({"error": "File not found"}), 404
    job = jobs.get(file_id, {})
    download_name = job.get("filename", "audio.mp3")
    return send_file(mp3_path, as_attachment=True, download_name=download_name, mimetype="audio/mpeg")


if __name__ == "__main__":
    print("🎵 MP3 Converter server running on http://localhost:5050")
    app.run(host="0.0.0.0", port=5050, debug=False)
