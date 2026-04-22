"""Integration tests for the `Recordings` model against a real in-memory SQLite DB."""

import datetime as dt

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.recordings import Recordings
from app.models.users import Users


def _make_user(test_db, *, username="alice") -> Users:
    user = Users(username=username, hashed_password="pw")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.mark.integration
class TestRecordingsModel:
    def test_insert_recording_sets_defaults(self, test_db):
        user = _make_user(test_db)

        rec = Recordings(
            user_id=user.id,
            target_name="Mom",
            to_number="+15555551234",
            audio=b"RIFF....WAVE-bytes",
        )
        test_db.add(rec)
        test_db.commit()
        test_db.refresh(rec)

        assert rec.id is not None
        assert rec.user_id == user.id
        assert rec.audio == b"RIFF....WAVE-bytes"
        assert isinstance(rec.created_at, dt.datetime)

    def test_nullable_constraints_reject_missing_required_fields(self, test_db):
        user = _make_user(test_db)

        test_db.add(
            Recordings(
                user_id=user.id,
                target_name=None,  # NOT NULL
                to_number="+1",
                audio=b"x",
            )
        )
        with pytest.raises(IntegrityError):
            test_db.commit()
        test_db.rollback()

    def test_audio_is_none_rejected(self, test_db):
        user = _make_user(test_db)

        test_db.add(
            Recordings(
                user_id=user.id,
                target_name="Mom",
                to_number="+1",
                audio=None,  # NOT NULL
            )
        )
        with pytest.raises(IntegrityError):
            test_db.commit()
        test_db.rollback()

    def test_delete_recording(self, test_db):
        user = _make_user(test_db)

        rec = Recordings(
            user_id=user.id,
            target_name="Mom",
            to_number="+1",
            audio=b"bytes",
        )
        test_db.add(rec)
        test_db.commit()
        rec_id = rec.id

        test_db.delete(rec)
        test_db.commit()

        assert test_db.query(Recordings).filter(Recordings.id == rec_id).first() is None

    def test_filter_by_user_isolates_recordings(self, test_db):
        alice = _make_user(test_db, username="alice")
        bob = _make_user(test_db, username="bob")

        test_db.add(
            Recordings(
                user_id=alice.id,
                target_name="Mom",
                to_number="+1",
                audio=b"a",
            )
        )
        test_db.add(
            Recordings(
                user_id=bob.id,
                target_name="Dad",
                to_number="+2",
                audio=b"b",
            )
        )
        test_db.commit()

        alice_recs = (
            test_db.query(Recordings).filter(Recordings.user_id == alice.id).all()
        )
        bob_recs = (
            test_db.query(Recordings).filter(Recordings.user_id == bob.id).all()
        )

        assert len(alice_recs) == 1 and alice_recs[0].target_name == "Mom"
        assert len(bob_recs) == 1 and bob_recs[0].target_name == "Dad"

    def test_order_by_created_at_desc(self, test_db):
        user = _make_user(test_db)

        now = dt.datetime.now()
        rec_old = Recordings(
            user_id=user.id,
            target_name="Old",
            to_number="+1",
            audio=b"a",
            created_at=now - dt.timedelta(days=1),
        )
        rec_new = Recordings(
            user_id=user.id,
            target_name="New",
            to_number="+2",
            audio=b"b",
            created_at=now,
        )
        test_db.add_all([rec_old, rec_new])
        test_db.commit()

        ordered = (
            test_db.query(Recordings)
            .filter(Recordings.user_id == user.id)
            .order_by(Recordings.created_at.desc())
            .all()
        )
        assert [r.target_name for r in ordered] == ["New", "Old"]
