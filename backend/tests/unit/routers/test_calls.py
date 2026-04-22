"""Unit tests for the `calls` router.

NOTE: Only the REST endpoints are tested. The WebSocket endpoint (`/ws`) and
the `/twiml` TwiML generator are intentionally skipped because they are part
of the pipeline / pipecat flow.
"""

from unittest.mock import MagicMock, patch

import pytest
from twilio.base.exceptions import TwilioRestException

from app.schemas.calls import TwilioCallResult


@pytest.mark.unit
class TestDialout:
    def test_dialout_success(self, client, mock_db):
        agent = MagicMock(id=1)

        async def _fake_make_twilio_call(user_id, agent_id, to_number, target_name):
            assert user_id == 1
            assert agent_id == "1"
            assert to_number == "+15555551234"
            assert target_name == "Mom"
            return TwilioCallResult(call_sid="CA123", to_number=to_number)

        with (
            patch("app.routers.calls.verify_agent", return_value=agent) as m_verify,
            patch(
                "app.routers.calls.make_twilio_call",
                side_effect=_fake_make_twilio_call,
            ) as m_make,
        ):
            resp = client.post(
                "/dialout",
                json={
                    "agent_id": "1",
                    "target_name": "Mom",
                    "to_number": "+15555551234",
                },
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body == {
            "call_sid": "CA123",
            "status": "call_initiated",
            "to_number": "+15555551234",
        }
        m_verify.assert_called_once_with("1", mock_db)
        m_make.assert_called_once()

    def test_dialout_missing_field_returns_422(self, client):
        resp = client.post(
            "/dialout",
            json={"agent_id": "1", "target_name": "Mom"},  # missing to_number
        )
        assert resp.status_code == 422


@pytest.mark.unit
class TestGetCallStatus:
    def test_get_call_status_success(self, client):
        fake_call = MagicMock(sid="CA123", status="in-progress", to="+15555551234")

        with patch("app.routers.calls.client") as mock_twilio:
            mock_twilio.calls.return_value.fetch.return_value = fake_call

            resp = client.get("/call/status", params={"call_sid": "CA123"})

        assert resp.status_code == 200
        assert resp.json() == {
            "call_sid": "CA123",
            "status": "in-progress",
            "to_number": "+15555551234",
        }

    def test_get_call_status_twilio_error_returns_500(self, client):
        with patch("app.routers.calls.client") as mock_twilio:
            mock_twilio.calls.return_value.fetch.side_effect = Exception("boom")

            resp = client.get("/call/status", params={"call_sid": "CA123"})

        assert resp.status_code == 500


@pytest.mark.unit
class TestCancelCall:
    @pytest.mark.parametrize(
        "current_status,expected_update_status",
        [
            ("queued", "canceled"),
            ("ringing", "canceled"),
            ("in-progress", "completed"),
            ("initiated", "completed"),
        ],
    )
    def test_cancel_active_call_maps_status_correctly(
        self, client, current_status, expected_update_status
    ):
        fetched = MagicMock(sid="CA123", status=current_status, to="+15555551234")
        updated = MagicMock(
            sid="CA123", status=expected_update_status, to="+15555551234"
        )

        with patch("app.routers.calls.client") as mock_twilio:
            mock_twilio.calls.return_value.fetch.return_value = fetched
            mock_twilio.calls.return_value.update.return_value = updated

            resp = client.post("/call/cancel", params={"call_sid": "CA123"})

        assert resp.status_code == 200
        assert resp.json()["status"] == expected_update_status
        mock_twilio.calls.return_value.update.assert_called_once_with(
            status=expected_update_status
        )

    @pytest.mark.parametrize(
        "terminal_status",
        ["completed", "canceled", "busy", "failed", "no-answer"],
    )
    def test_cancel_already_terminal_call_returns_current_status_without_update(
        self, client, terminal_status
    ):
        fetched = MagicMock(sid="CA123", status=terminal_status, to="+15555551234")

        with patch("app.routers.calls.client") as mock_twilio:
            mock_twilio.calls.return_value.fetch.return_value = fetched

            resp = client.post("/call/cancel", params={"call_sid": "CA123"})

        assert resp.status_code == 200
        assert resp.json()["status"] == terminal_status
        mock_twilio.calls.return_value.update.assert_not_called()

    def test_cancel_twilio_error_returns_400(self, client):
        with patch("app.routers.calls.client") as mock_twilio:
            mock_twilio.calls.return_value.fetch.side_effect = TwilioRestException(
                status=400, uri="/", msg="bad"
            )
            resp = client.post("/call/cancel", params={"call_sid": "CA123"})
        assert resp.status_code == 400

    def test_cancel_generic_error_returns_500(self, client):
        with patch("app.routers.calls.client") as mock_twilio:
            mock_twilio.calls.return_value.fetch.side_effect = RuntimeError("boom")
            resp = client.post("/call/cancel", params={"call_sid": "CA123"})
        assert resp.status_code == 500
        assert resp.json()["detail"] == "Internal server error"
