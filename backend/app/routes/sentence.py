"""
sentence.py (routes)
=====================
Session-scoped sentence builder: create / add / space / backspace / clear / get.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SentenceCreateResponse, SentenceAddRequest, SentenceResponse, SessionIdRequest
from app.services import sentence_builder

router = APIRouter(prefix="/sentence", tags=["sentence"])


@router.post("/create", response_model=SentenceCreateResponse)
def create_sentence_session(db: Session = Depends(get_db)):
    session = sentence_builder.create_session(db)
    return SentenceCreateResponse(session_id=session.session_id, sentence=session.sentence or "")


@router.post("/add", response_model=SentenceResponse)
def add_character(payload: SentenceAddRequest, db: Session = Depends(get_db)):
    sentence = sentence_builder.add_character(db, payload.session_id, payload.character)
    return SentenceResponse(session_id=payload.session_id, sentence=sentence)


@router.post("/space", response_model=SentenceResponse)
def add_space(payload: SessionIdRequest, db: Session = Depends(get_db)):
    sentence = sentence_builder.add_space(db, payload.session_id)
    return SentenceResponse(session_id=payload.session_id, sentence=sentence)


@router.post("/backspace", response_model=SentenceResponse)
def do_backspace(payload: SessionIdRequest, db: Session = Depends(get_db)):
    sentence = sentence_builder.backspace(db, payload.session_id)
    return SentenceResponse(session_id=payload.session_id, sentence=sentence)


@router.post("/clear", response_model=SentenceResponse)
def clear_sentence(payload: SessionIdRequest, db: Session = Depends(get_db)):
    sentence = sentence_builder.clear_sentence(db, payload.session_id)
    return SentenceResponse(session_id=payload.session_id, sentence=sentence)


@router.get("/{session_id}", response_model=SentenceResponse)
def get_sentence(session_id: str, db: Session = Depends(get_db)):
    sentence = sentence_builder.get_sentence(db, session_id)
    return SentenceResponse(session_id=session_id, sentence=sentence)
