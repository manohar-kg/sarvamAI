# 🎙️ Build a Speech-to-Text Transcriber with Sarvam AI in Python

This tutorial will guide you step-by-step in building a **Speech-to-Text transcriber** using [Sarvam AI’s speech-to-text API](https://sarvam.ai/). The app supports long audio files by automatically splitting them into chunks and transcribing each segment. All transcripts are combined and saved into a CSV file.

---

## 🗂️ Project Directory Structure

```
SarvamAI/
│
├── outputs/               # Folder to save output transcripts
├── .env                   # Environment file to store your API key
├── main.py                # Main Python script
└── requirements.txt       # List of Python dependencies
```

---

## 🔐 Step 1: Get Your API Key

1. Go to [https://sarvam.ai](https://sarvam.ai) and sign up.
2. Generate your API key for speech-to-text.
3. Create a `.env` file in the root folder and add the following line:

```env
SARVAM_AI_API="your-sarvam-api-key-here"
```

---

## 📦 Step 2: Install Required Packages

Create a `requirements.txt` file with the following content:

```txt
requests
pandas
pydub
python-dotenv
```

Then run:

```bash
pip install -r requirements.txt
```

> ⚠️ Make sure `ffmpeg` is installed on your system for `pydub` to process audio files.

---

## 🧠 Step 3: Full Code (`main.py`)

Create a file named `main.py` and paste the following complete script:

```python
import os
import io
import requests
import logging
import pandas as pd
from pydub import AudioSegment
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# API key setup
SARVAM_AI_API_KEY = os.getenv("SARVAM_AI_API")
if not SARVAM_AI_API_KEY:
    raise EnvironmentError("SARVAM_AI_API environment variable not set.")

# Constants
API_URL = "https://api.sarvam.ai/speech-to-text"
HEADERS = {"api-subscription-key": SARVAM_AI_API_KEY}
DEFAULT_MODEL = "saarika:v2"
DEFAULT_LANG = "hi-IN"
DEFAULT_CHUNK_MS = 5 * 60 * 1000  # 5 minutes

# Audio splitter
def split_audio(audio_path, chunk_duration_ms):
    audio = AudioSegment.from_file(audio_path)
    return [audio[i:i + chunk_duration_ms] for i in range(0, len(audio), chunk_duration_ms)]

# Transcribe a chunk
def transcribe_chunk(chunk, index, api_url, headers, payload):
    buffer = io.BytesIO()
    chunk.export(buffer, format="wav")
    buffer.seek(0)
    files = {'file': ('audio.wav', buffer, 'audio/wav')}

    try:
        response = requests.post(api_url, headers=headers, files=files, data=payload)
        if response.ok:
            logging.info(f"Chunk {index} transcribed successfully.")
            return response.json().get("transcript", "")
        else:
            logging.error(f"Chunk {index} failed: {response.status_code}")
    except Exception as e:
        logging.error(f"Chunk {index} error: {e}")
    finally:
        buffer.close()
    return ""

# Transcribe full file
def transcribe_audio_file(audio_file_path, model, lang, chunk_ms):
    chunks = split_audio(audio_file_path, chunk_ms)
    payload = {"language_code": lang, "model": model, "with_timestamps": False}
    transcripts = [transcribe_chunk(chunk, idx, API_URL, HEADERS, payload) for idx, chunk in enumerate(chunks)]
    return " ".join(transcripts).strip()

# Main execution
def main():
    input_path = "data/Recording2.wav"  # Update path as needed
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"outputs/transcription_{timestamp}.csv"

    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    logging.info("Starting transcription...")
    transcription = transcribe_audio_file(input_path, DEFAULT_MODEL, DEFAULT_LANG, DEFAULT_CHUNK_MS)

    if transcription:
        pd.DataFrame({"collated_transcript": [transcription]}).to_csv(output_path, index=False)
        logging.info(f"Saved transcription to: {output_path}")
        print(transcription)  # Print the transcription to console
    else:
        logging.warning("No transcription produced.")

if __name__ == "__main__":
    main()
```

---

## ▶️ Step 4: Run the Script

1. Place your `.wav` audio file in a folder named `data/` and rename it `Recording2.wav`.
2. Run the script:

```bash
python main.py
```

You’ll see output in the console and a `.csv` file saved in the `outputs/` folder.

---

## ✅ Output Example

```
2025-05-28 10:45:22 [INFO] Starting transcription...
2025-05-28 10:45:35 [INFO] Chunk 0 transcribed successfully.
2025-05-28 10:45:36 [INFO] Saved transcription to: outputs/transcription_20250528_104536.csv
```

## 🏁 Wrap-Up

You now have a working Python app that converts speech to text using Sarvam AI. This setup is great for transcribing interviews, meetings, or voice notes—especially in Indian languages.