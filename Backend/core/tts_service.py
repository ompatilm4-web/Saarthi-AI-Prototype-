import os
import asyncio
import hashlib
import tempfile
import logging
from typing import Optional

logger = logging.getLogger(__name__)

LANGUAGE_CONFIG = {
    "hi": {"gtts_code": "hi", "edge_voice": "hi-IN-SwaraNeural"},
    "en": {"gtts_code": "en", "edge_voice": "en-IN-NeerjaNeural"},
    "ta": {"gtts_code": "ta", "edge_voice": "ta-IN-PallaviNeural"},
    "te": {"gtts_code": "te", "edge_voice": "te-IN-ShrutiNeural"},
    "bn": {"gtts_code": "bn", "edge_voice": "bn-IN-TanishaaNeural"},
    "mr": {"gtts_code": "mr", "edge_voice": "mr-IN-AarohiNeural"},
    "gu": {"gtts_code": "gu", "edge_voice": "gu-IN-DhwaniNeural"},
    "kn": {"gtts_code": "kn", "edge_voice": "kn-IN-SapnaNeural"},
    "ml": {"gtts_code": "ml", "edge_voice": "ml-IN-SobhanaNeural"},
    "pa": {"gtts_code": "pa", "edge_voice": "pa-IN-OjasNeural"},
    "ur": {"gtts_code": "ur", "edge_voice": "ur-IN-GulNeural"},
}

class TTSService:
    def __init__(self):
        self.default_lang = os.getenv("TTS_DEFAULT_LANG", "hi")
        self._cache = {}

    def get_supported_languages(self):
        return list(LANGUAGE_CONFIG.keys())

    def estimate_speaking_duration(self, text: str, lang: str = "hi") -> float:
        words = len(text.split())
        wpm = 130 if lang == "hi" else 150
        return round((words / wpm) * 60, 1)

    async def synthesize(self, text: str, lang: str = "hi", output_format: str = "base64") -> Optional[dict]:
        if not text or not text.strip():
            return None
        lang = lang if lang in LANGUAGE_CONFIG else self.default_lang
        cache_key = hashlib.md5(f"{lang}:{text[:100]}".encode()).hexdigest()
        if cache_key in self._cache:
            return self._cache[cache_key]
        result = await self._try_edge_tts(text, lang, output_format)
        if not result:
            result = await self._try_gtts(text, lang, output_format)
        if result:
            self._cache[cache_key] = result
        return result

    async def _try_edge_tts(self, text: str, lang: str, output_format: str) -> Optional[dict]:
        try:
            import edge_tts
            voice = LANGUAGE_CONFIG[lang]["edge_voice"]
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp_path = f.name
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(tmp_path)
            if output_format == "base64":
                import base64
                with open(tmp_path, "rb") as f:
                    audio_b64 = base64.b64encode(f.read()).decode()
                os.unlink(tmp_path)
                return {"audio": audio_b64, "format": "base64", "engine": "edge"}
            return {"audio": tmp_path, "format": "file", "engine": "edge"}
        except Exception as e:
            logger.warning(f"Edge TTS failed: {e}")
            return None

    async def _try_gtts(self, text: str, lang: str, output_format: str) -> Optional[dict]:
        try:
            from gtts import gTTS
            import base64
            gtts_code = LANGUAGE_CONFIG.get(lang, {}).get("gtts_code", "hi")
            tts = gTTS(text=text[:500], lang=gtts_code, slow=False)
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp_path = f.name
            tts.save(tmp_path)
            if output_format == "base64":
                with open(tmp_path, "rb") as f:
                    audio_b64 = base64.b64encode(f.read()).decode()
                os.unlink(tmp_path)
                return {"audio": audio_b64, "format": "base64", "engine": "gtts"}
            return {"audio": tmp_path, "format": "file", "engine": "gtts"}
        except Exception as e:
            logger.warning(f"gTTS failed: {e}")
            return None

_tts_service = None

def get_tts_service() -> TTSService:
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service

async def text_to_speech(text: str, lang: str = "hi", output_format: str = "base64") -> Optional[dict]:
    service = get_tts_service()
    return await service.synthesize(text, lang, output_format)
