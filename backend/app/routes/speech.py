"""
speech.py (routes)
===================
POST /speak - offline TTS for the current sentence.
"""

from fastapi import APIRouter, HTTPException

from app.schemas import SpeakRequest, SpeakResponse
from app.services import speech as speech_service

router = APIRouter(tags=["speech"])


@router.post("/speak", response_model=SpeakResponse)
def speak(payload: SpeakRequest):
    try:
        speech_service.speak(payload.text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return SpeakResponse(status="ok", text=payload.text)
