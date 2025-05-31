# 🧠 Build a Speech-to-Text Transcriber with Sarvam AI and Python — A Complete Step-by-Step Guide

Transcribing long audio recordings - especially in Indian languages - can be tedious and time consuming. Whether you're dealing with meeting recordings, interviews, or academic lectures, automation is the key.

In this guide, you'll build a complete Speech-to-Text transcriber using Python and Sarvam AI's API. We'll walk through everything - from setting up your project to understanding each line of code - so you not only know **how** it works but also **why** it works.

---

## ✅ Prerequisites

Before getting started, make sure you have the following:

* Python 3.8 or higher installed
* Basic familiarity with using the terminal/command prompt
* Git installed (optional, for cloning a GitHub repo)
* An audio file in `.wav` format (you can convert from `.mp3` using [pydub](https://github.com/jiaaro/pydub))
* A Sarvam AI account with access to its Speech-to-Text API

---

## 🗂️ Step 1: Project Setup

Create a project folder with the following structure:

```
SarvamAI/
├── data/                 # Place your input audio files here
├── outputs/              # Transcripts will be saved here
├── .env                  # Contains your Sarvam AI API key
├── main.py               # Main script containing all logic
└── requirements.txt      # List of required packages
```

---

## 🔐 Step 2: Get Your Sarvam AI API Key

1. Sign up at [sarvam.ai](https://sarvam.ai)
2. Navigate to the developer dashboard and generate a Speech-to-Text API key
3. In the root of your project, create a `.env` file with the following content:

```env
SARVAM_AI_API="your-sarvam-api-key-here"
```

We’ll use `python-dotenv` to load this key securely into the Python script.

---

## 🧰 Step 3: (Recommended) Use a Virtual Environment

To avoid dependency conflicts and keep things organized, set up a virtual environment.

### Create a virtual environment:

```bash
python -m venv venv
```

### Activate the environment:

* **Windows:** `venv\Scripts\activate`
* **macOS/Linux:** `source venv/bin/activate`

You’ll now see `(venv)` prefixed in your terminal, indicating the environment is active.

---

## 📦 Step 4: Install Dependencies

Create a `requirements.txt` file with the following:

```
requests
pandas
pydub
python-dotenv
```

Install the packages using:

```bash
pip install -r requirements.txt
```

✅ *Why this matters*: Virtual environments keep dependencies project-specific, ensuring reproducibility and cleaner setups across machines.

---

## 🧠 Step 5: Write and Understand the Code

Create a file called `main.py`. Here's a breakdown of the full script and what each part does:

---

### 🔹 Imports & Environment Setup

```python
import os, io, requests, logging
import pandas as pd
from pydub import AudioSegment
from datetime import datetime
from dotenv import load_dotenv
```

* `pydub` handles audio file processing
* `requests` sends files to Sarvam AI
* `pandas` saves the transcript
* `dotenv` loads the API key

---

### 🔹 Load API Key and Define Constants

```python
load_dotenv()
SARVAM_AI_API_KEY = os.getenv("SARVAM_AI_API")

if not SARVAM_AI_API_KEY:
    raise EnvironmentError("SARVAM_AI_API not found in .env file.")

API_URL = "https://api.sarvam.ai/speech-to-text"
HEADERS = {"api-subscription-key": SARVAM_AI_API_KEY}
DEFAULT_MODEL = "saarika:v2"
DEFAULT_LANG = "hi-IN"
DEFAULT_CHUNK_MS = 5 * 60 * 1000  # 5 minutes
```

---

### 🔹 Configure Logging

```python
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
```

Logging is useful for tracking transcription progress and errors.

---

### 🔹 Split Audio into Chunks

```python
def split_audio(audio_path, chunk_duration_ms):
    audio = AudioSegment.from_file(audio_path)
    return [audio[i:i + chunk_duration_ms] for i in range(0, len(audio), chunk_duration_ms)]
```

Splitting audio helps prevent timeouts with long files.

---

### 🔹 Send Audio Chunk to API

```python
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
            logging.error(f"Chunk {index} failed with status: {response.status_code}")
    except Exception as e:
        logging.error(f"Chunk {index} error: {e}")
    finally:
        buffer.close()

    return ""
```

Each chunk is converted to a WAV byte stream and sent to Sarvam's API. The returned transcript is extracted from the response.

---

### 🔹 Transcribe the Full Audio

```python
def transcribe_audio_file(audio_file_path, model, lang, chunk_ms):
    chunks = split_audio(audio_file_path, chunk_ms)
    payload = {"language_code": lang, "model": model, "with_timestamps": False}
    transcripts = [
        transcribe_chunk(chunk, idx, API_URL, HEADERS, payload)
        for idx, chunk in enumerate(chunks)
    ]
    return " ".join(transcripts).strip()
```

This combines all chunk transcripts into a single string.

---

### 🔹 Main Script Logic

```python
def main():
    input_path = "data/Recording2.wav"
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"outputs/transcription_{timestamp}.csv"

    logging.info("Starting transcription...")

    transcription = transcribe_audio_file(
        audio_file_path=input_path,
        model=DEFAULT_MODEL,
        lang=DEFAULT_LANG,
        chunk_ms=DEFAULT_CHUNK_MS
    )

    if transcription:
        pd.DataFrame({"collated_transcript": [transcription]}).to_csv(output_path, index=False)
        logging.info(f"Transcription saved to: {output_path}")
        print(transcription)
    else:
        logging.warning("No transcription generated.")
```

---

### 🔹 Run the Script

```python
if __name__ == "__main__":
    main()
```

This ensures the script runs only when executed directly (not when imported).

---

## ▶️ Step 6: Run Your Transcriber

1. Place your `.wav` file in the `data/` folder
2. Run the script:

```bash
python main.py
```

---

## ✅ Sample Console Output

```
2025-05-28 10:45:22 [INFO] Starting transcription...
2025-05-28 10:45:35 [INFO] Chunk 0 transcribed successfully.
2025-05-28 10:45:36 [INFO] Transcription saved to: outputs/transcription_20250528_104536.csv
```

---

## 💡 Real-World Use Cases

* Journalists transcribing field interviews
* Students converting lectures into notes
* Product teams documenting user research or meetings
* Developers building voice-enabled apps for Indian languages

---

## 🧾 GitHub Source Code

🔗 Get the complete source code and sample files here:
👉 [GitHub Repository: SarvamAI Speech-to-Text Transcriber](https://github.com/manohar-kg/sarvamAI/tree/main))

**Pro Tip:** Clone the repo, install the dependencies, and you're ready to start transcribing!

If this guide helped you, consider starring the GitHub repo and sharing it with others.

---
