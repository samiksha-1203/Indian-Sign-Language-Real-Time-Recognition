"""
test_sentence_builder.py
=========================
Tests: A -> A B -> A SPACE B -> BACKSPACE -> CLEAR, against an in-memory
SQLite database (isolated from the real signspeak.db).
"""

import sys
import uuid
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.database import Base  # noqa: E402
from app.services import sentence_builder  # noqa: E402


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(bind=engine)
    session = TestSessionLocal()
    yield session
    session.close()


def test_add_character(db_session):
    sid = str(uuid.uuid4())
    result = sentence_builder.add_character(db_session, sid, "A")
    assert result == "A"


def test_add_multiple_characters(db_session):
    sid = str(uuid.uuid4())
    sentence_builder.add_character(db_session, sid, "A")
    result = sentence_builder.add_character(db_session, sid, "B")
    assert result == "AB"


def test_add_space_between_words(db_session):
    sid = str(uuid.uuid4())
    sentence_builder.add_character(db_session, sid, "A")
    sentence_builder.add_space(db_session, sid)
    result = sentence_builder.add_character(db_session, sid, "B")
    assert result == "A B"


def test_backspace_removes_last_character(db_session):
    sid = str(uuid.uuid4())
    sentence_builder.add_character(db_session, sid, "A")
    sentence_builder.add_character(db_session, sid, "B")
    result = sentence_builder.backspace(db_session, sid)
    assert result == "A"


def test_backspace_on_empty_sentence_stays_empty(db_session):
    sid = str(uuid.uuid4())
    result = sentence_builder.backspace(db_session, sid)
    assert result == ""


def test_clear_resets_sentence(db_session):
    sid = str(uuid.uuid4())
    sentence_builder.add_character(db_session, sid, "H")
    sentence_builder.add_character(db_session, sid, "I")
    result = sentence_builder.clear_sentence(db_session, sid)
    assert result == ""


def test_get_sentence_creates_session_if_missing(db_session):
    sid = str(uuid.uuid4())
    result = sentence_builder.get_sentence(db_session, sid)
    assert result == ""


def test_sessions_are_isolated(db_session):
    sid1, sid2 = str(uuid.uuid4()), str(uuid.uuid4())
    sentence_builder.add_character(db_session, sid1, "A")
    sentence_builder.add_character(db_session, sid2, "Z")
    assert sentence_builder.get_sentence(db_session, sid1) == "A"
    assert sentence_builder.get_sentence(db_session, sid2) == "Z"
