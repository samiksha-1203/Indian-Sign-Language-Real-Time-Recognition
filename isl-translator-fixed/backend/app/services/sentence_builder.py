"""
sentence_builder.py (service)
==============================
Turns a stream of confirmed characters into an editable sentence, backed by
the `sessions` SQLite table so a sentence survives across requests.
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.database import SignSession


def create_session(db: Session) -> SignSession:
    session_id = str(uuid.uuid4())
    session = SignSession(session_id=session_id, start_time=datetime.utcnow(), sentence="")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_or_create_session(db: Session, session_id: str) -> SignSession:
    session = db.query(SignSession).filter(SignSession.session_id == session_id).first()
    if session is None:
        session = SignSession(session_id=session_id, start_time=datetime.utcnow(), sentence="")
        db.add(session)
        db.commit()
        db.refresh(session)
    return session


def add_character(db: Session, session_id: str, character: str) -> str:
    session = get_or_create_session(db, session_id)
    session.sentence = (session.sentence or "") + character
    db.commit()
    return session.sentence


def add_space(db: Session, session_id: str) -> str:
    return add_character(db, session_id, " ")


def backspace(db: Session, session_id: str) -> str:
    session = get_or_create_session(db, session_id)
    session.sentence = (session.sentence or "")[:-1]
    db.commit()
    return session.sentence


def clear_sentence(db: Session, session_id: str) -> str:
    session = get_or_create_session(db, session_id)
    session.sentence = ""
    db.commit()
    return session.sentence


def get_sentence(db: Session, session_id: str) -> str:
    session = get_or_create_session(db, session_id)
    return session.sentence or ""
