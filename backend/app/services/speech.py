"""
speech.py (service)
====================
Local, offline text-to-speech using pyttsx3. No cloud calls, no API keys.
"""

from threading import Lock

_engine = None
_engine_lock = Lock()
_init_error = None


def _get_engine():
    global _engine, _init_error
    if _engine is None and _init_error is None:
        try:
            import pyttsx3
            _engine = pyttsx3.init()
        except Exception as e:
            _init_error = str(e)
    return _engine


def speak(text: str):
    """Speaks text synchronously (blocking). Called from a request handler,
    so keep sentences short; this is acceptable for a demo/desktop-style app.
    """
    if not text or not text.strip():
        raise ValueError("No text to speak.")

    with _engine_lock:
        engine = _get_engine()
        if engine is None:
            raise RuntimeError(
                f"TTS engine unavailable: {_init_error}. "
                f"Ensure pyttsx3 and a system TTS backend (e.g. espeak on Linux, "
                f"SAPI5 on Windows) are installed."
            )
        engine.say(text)
        engine.runAndWait()
