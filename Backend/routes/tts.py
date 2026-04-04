"""
routes/tts.py — Edge TTS endpoint
Converts text to speech using Microsoft Edge TTS (free, supports all Indian languages)
"""
import asyncio, base64, os, tempfile
import edge_tts
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()

# Best Edge TTS voices for Indian languages
VOICE_MAP = {
    "hi":  "hi-IN-SwaraNeural",      # Hindi - female
    "en":  "en-IN-NeerjaNeural",     # English India - female
    "mr":  "mr-IN-AarohiNeural",     # Marathi - female
    "bn":  "bn-IN-TanishaaNeural",   # Bengali - female
    "ta":  "ta-IN-PallaviNeural",    # Tamil - female
    "te":  "te-IN-ShrutiNeural",     # Telugu - female
    "gu":  "gu-IN-DhwaniNeural",     # Gujarati - female
    "kn":  "kn-IN-SapnaNeural",      # Kannada - female
    "ml":  "ml-IN-SobhanaNeural",    # Malayalam - female
    "pa":  "pa-IN-OjasNeural",       # Punjabi - male (no female available)
}

class TTSRequest(BaseModel):
    text: str
    lang: str = "hi"

@router.post("/tts")
async def text_to_speech(req: TTSRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    # Clean text
    clean = req.text.strip()[:500]  # limit to 500 chars for TTS
    voice = VOICE_MAP.get(req.lang, VOICE_MAP["hi"])

    try:
        # Generate speech to a temp file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name

        communicate = edge_tts.Communicate(clean, voice)
        await communicate.save(tmp_path)

        # Read and encode as base64
        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
        os.unlink(tmp_path)

        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        return {"audio": audio_b64, "voice": voice, "lang": req.lang}

    except Exception as e:
        print(f"[Edge TTS Error]: {e}")
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")
