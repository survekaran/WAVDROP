# 🎵 WAVDROP — Video to MP3 Converter

WAVDROP is a full-stack web application that converts YouTube links and video files into high-quality MP3 audio. It supports multiple formats, real-time progress tracking, and a modern user interface.

---

## 🚀 Features

* Convert YouTube / video URLs to MP3
* Upload local video/audio files for conversion
* Select audio quality (320kbps / 192kbps / 128kbps)
* Real-time conversion progress tracking
* Fast and asynchronous processing
* Drag-and-drop file upload
* Automatic cleanup of old files

---

## 🛠️ Tech Stack

### Frontend

* HTML5
* CSS3
* JavaScript

### Backend

* Python (Flask)
* yt-dlp
* FFmpeg
* Flask-CORS

---

## 📂 Project Structure

```
wavdrop/
│
├── index.html
├── server.py
├── uploads/
├── outputs/
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```
git clone https://github.com/your-username/wavdrop.git
cd wavdrop
```

---

### 2. Install Python Dependencies

```
pip install flask flask-cors yt-dlp
```

---

### 3. Install FFmpeg

Download and install FFmpeg, then add it to your system PATH.

Check installation:

```
ffmpeg -version
```

---

### 4. Run Backend Server

```
python server.py
```

Server will run on:

```
http://localhost:5050
```

---

### 5. Run Frontend

Open `index.html` in your browser.

---

## 🔄 How It Works

### URL Conversion

1. Paste a YouTube or video URL
2. Select quality
3. Click convert
4. Download MP3

### File Conversion

1. Upload or drag a file
2. Select quality
3. Convert to MP3
4. Download result

---

## 📡 API Endpoints

| Endpoint                | Method | Description           |
| ----------------------- | ------ | --------------------- |
| /api/convert/url        | POST   | Convert YouTube URL   |
| /api/convert/file       | POST   | Convert uploaded file |
| /api/status/<job_id>    | GET    | Get job progress      |
| /api/download/<file_id> | GET    | Download MP3          |

---

## ⚡ Core Functionality

* Uses yt-dlp to extract audio from YouTube
* Uses FFmpeg for MP3 conversion
* Background threads handle conversion jobs
* Frontend polls backend for progress updates

---

## ⚠️ Disclaimer

This project is for educational purposes only. Ensure you follow copyright laws when downloading content.

---

## 👨‍💻 Author

Karan Surve

---

## ⭐ Support

If you found this project useful, consider giving it a star on GitHub.
