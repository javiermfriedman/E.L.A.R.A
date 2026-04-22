"""Unit tests for the `recordings` router."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest


def _make_recording_row(
    *,
    id: int = 1,
    user_id: int = 1,
    target_name: str = "Mom",
    to_number: str = "+15555551234",
    audio: bytes = b"RIFF....WAVEfake",
    created_at: datetime | None = None,
) -> MagicMock:
    rec = MagicMock()
    rec.id = id
    rec.user_id = user_id
    rec.target_name = target_name
    rec.to_number = to_number
    rec.audio = audio
    rec.created_at = created_at or datetime(2026, 1, 1, 12, 0, 0)
    return rec


@pytest.mark.unit
class TestGetRecordings:
    def test_get_recordings_returns_list(self, client, mock_db):
        recs = [_make_recording_row(id=1), _make_recording_row(id=2, target_name="Dad")]
        chain = mock_db.query.return_value.filter.return_value.order_by.return_value
        chain.all.return_value = recs

        resp = client.get("/recordings/")

        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 2
        assert body[0]["target_name"] == "Mom"
        assert body[1]["target_name"] == "Dad"
        # Audio must NOT be serialized in the list response
        assert "audio" not in body[0]

    def test_get_recordings_empty(self, client, mock_db):
        chain = mock_db.query.return_value.filter.return_value.order_by.return_value
        chain.all.return_value = []

        resp = client.get("/recordings/")

        assert resp.status_code == 200
        assert resp.json() == []


@pytest.mark.unit
class TestGetRecordingAudio:
    def test_get_recording_audio_success(self, client, mock_db):
        rec = _make_recording_row(id=5, audio=b"RIFF....WAVE-audio")
        mock_db.query.return_value.filter.return_value.first.return_value = rec

        resp = client.get("/recordings/5/audio")

        assert resp.status_code == 200
        assert resp.content == b"RIFF....WAVE-audio"
        assert resp.headers["content-type"] == "audio/wav"
        assert 'recording-5.wav' in resp.headers["content-disposition"]

    def test_get_recording_audio_not_found(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        resp = client.get("/recordings/999/audio")

        assert resp.status_code == 404
        assert resp.json()["detail"] == "Recording not found"


@pytest.mark.unit
class TestDeleteRecordings:
    def test_delete_all_recordings(self, client, mock_db):
        recs = [_make_recording_row(id=1), _make_recording_row(id=2)]
        mock_db.query.return_value.filter.return_value.all.return_value = recs

        resp = client.delete("/recordings/")

        assert resp.status_code == 200
        assert resp.json() == {"message": "All recordings deleted successfully"}
        assert mock_db.delete.call_count == 2
        mock_db.commit.assert_called_once()


@pytest.mark.unit
class TestDeleteRecordingById:
    def test_delete_recording_success(self, client, mock_db):
        rec = _make_recording_row(id=7)
        mock_db.query.return_value.filter.return_value.first.return_value = rec

        resp = client.delete("/recordings/7")

        assert resp.status_code == 200
        assert "7" in resp.json()["message"]
        mock_db.delete.assert_called_once_with(rec)
        mock_db.commit.assert_called_once()

    def test_delete_recording_not_found(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        resp = client.delete("/recordings/999")

        assert resp.status_code == 404
        assert resp.json()["detail"] == "Recording not found"
        mock_db.delete.assert_not_called()
