# Imports & Environment Setup
import os, io, requests, logging
import pandas as pd
from pydub import AudioSegment
from datetime import datetime
from dotenv import load_dotenv

# Load API Key and Define Constants
load_dotenv()
SARVAM_AI_API_KEY = os.getenv("SARVAM_AI_API")

if not SARVAM_AI_API_KEY:
    raise EnvironmentError("SARVAM_AI_API not found in .env file.")

API_URL = "https://api.sarvam.ai/speech-to-text"
HEADERS = {"api-subscription-key": SARVAM_AI_API_KEY}
DEFAULT_MODEL = "saarika:v2"
DEFAULT_LANG = "hi-IN"
DEFAULT_CHUNK_MS = 5 * 60 * 1000  # 5 minutes

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Split Audio into Chunks
def split_audio(audio_path, chunk_duration_ms):
    audio = AudioSegment.from_file(audio_path)
    return [audio[i:i + chunk_duration_ms] for i in range(0, len(audio), chunk_duration_ms)]

# Send Audio Chunk to API
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
            logging.error(f"Chunk {index} failed with status: {response.text}")
    except Exception as e:
        logging.error(f"Chunk {index} error: {e}")
    finally:
        buffer.close()

    return ""

# Transcribe the Full Audio
def transcribe_audio_file(audio_file_path, model, lang, chunk_ms):
    chunks = split_audio(audio_file_path, chunk_ms)
    payload = {"language_code": lang, "model": model, "with_timestamps": False}
    transcripts = [
        transcribe_chunk(chunk, idx, API_URL, HEADERS, payload)
        for idx, chunk in enumerate(chunks)
    ]
    return " ".join(transcripts).strip()

# Main Script Logic
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

if __name__ == "__main__":
    main()
