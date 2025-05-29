# main.py

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
    input_path = "data/Recording2.wav"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"outputs/transcription_{timestamp}.csv"

    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    logging.info("Starting transcription...")
    transcription = transcribe_audio_file(input_path, DEFAULT_MODEL, DEFAULT_LANG, DEFAULT_CHUNK_MS)

    if transcription:
        pd.DataFrame({"collated_transcript": [transcription]}).to_csv(output_path, index=False)
        logging.info(f"Saved transcription to: {output_path}")
        print(transcription)                                            # Print the transcription to console
    else:
        logging.warning("No transcription produced.")

if __name__ == "__main__":
    main()
