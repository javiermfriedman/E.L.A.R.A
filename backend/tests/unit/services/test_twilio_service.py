"""Unit tests for `app.services.twilio_service`.

The Twilio SDK is fully mocked; no network calls happen.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services.twilio_service import (
    generate_twiml,
    get_websocket_url,
    make_twilio_call,
    parse_twiml_request,
    verify_agent,
)
from app.schemas.calls import TwimlRequest


@pytest.mark.unit
class TestVerifyAgent:
    def test_verify_agent_success(self):
        from datetime import datetime

        agent = MagicMock()
        agent.id = 1
        agent.name = "Zeus"
        agent.description = "desc"
        agent.system_prompt = "sp"
        agent.first_message = "hi"
        agent.voice_id = "v1"
        agent.image_data = b"\x89PNG"
        agent.image_filename = "zeus.png"
        agent.created_at = datetime(2026, 1, 1, 12, 0, 0)
        import base64
        agent.image = base64.b64encode(b"\x89PNG").decode()

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = agent

        result = verify_agent("1", db)

        assert result.id == 1
        assert result.name == "Zeus"

    def test_verify_agent_not_found_raises_404(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            verify_agent("999", db)
        assert exc_info.value.status_code == 404


@pytest.mark.unit
class TestMakeTwilioCall:
    async def test_make_twilio_call_success(self):
        fake_call = MagicMock(sid="CA123")

        with patch("app.services.twilio_service.TwilioClient") as MockClient:
            instance = MockClient.return_value
            instance.calls.create.return_value = fake_call

            result = await make_twilio_call(
                user_id=1,
                agent_id="7",
                to_number="+15555551234",
                target_name="Mom",
            )

        assert result.call_sid == "CA123"
        assert result.to_number == "+15555551234"

        MockClient.assert_called_once_with("ACtestsid", "testtoken")
        _, kwargs = instance.calls.create.call_args
        assert kwargs["to"] == "+15555551234"
        assert kwargs["from_"] == "+15555550123"
        assert "agent_id=7" in kwargs["url"]
        assert "user_id=1" in kwargs["url"]
        assert "target_name=Mom" in kwargs["url"]
        assert kwargs["method"] == "POST"

    async def test_make_twilio_call_missing_local_server_url(self, monkeypatch):
        monkeypatch.delenv("LOCAL_SERVER_URL", raising=False)

        with pytest.raises(ValueError, match="LOCAL_SERVER_URL"):
            await make_twilio_call(1, "1", "+15555551234", "Mom")

    async def test_make_twilio_call_missing_twilio_credentials(self, monkeypatch):
        monkeypatch.delenv("TWILIO_ACCOUNT_SID", raising=False)

        with pytest.raises(ValueError, match="Twilio credentials"):
            await make_twilio_call(1, "1", "+15555551234", "Mom")


@pytest.mark.unit
class TestParseTwimlRequest:
    async def test_parse_twiml_request_extracts_form_fields(self):
        form_data = {"To": "+15555551234", "From": "+15555550123"}

        request = MagicMock()
        request.form = AsyncMock(return_value=form_data)

        result = await parse_twiml_request(request)

        assert isinstance(result, TwimlRequest)
        assert result.to_number == "+15555551234"
        assert result.from_number == "+15555550123"


@pytest.mark.unit
class TestGetWebsocketUrl:
    def test_local_env_returns_wss_from_local_server_url(self, monkeypatch):
        monkeypatch.setenv("ENV", "local")
        monkeypatch.setenv("LOCAL_SERVER_URL", "https://abc.ngrok.app")

        assert get_websocket_url() == "wss://abc.ngrok.app/ws"

    def test_local_env_missing_url_raises(self, monkeypatch):
        monkeypatch.setenv("ENV", "local")
        monkeypatch.delenv("LOCAL_SERVER_URL", raising=False)

        with pytest.raises(ValueError, match="LOCAL_SERVER_URL"):
            get_websocket_url()

    def test_non_local_env_returns_pipecat_cloud_url(self, monkeypatch):
        monkeypatch.setenv("ENV", "production")
        url = get_websocket_url()
        assert url.startswith("wss://")
        assert "pipecat" in url


@pytest.mark.unit
class TestGenerateTwiml:
    def test_generate_twiml_includes_expected_parameters(self, monkeypatch):
        monkeypatch.setenv("ENV", "local")
        monkeypatch.setenv("LOCAL_SERVER_URL", "https://abc.ngrok.app")

        req = TwimlRequest(to_number="+15555551234", from_number="+15555550123")
        xml = generate_twiml(req, agent_id="7", user_id="1", target_name="Mom")

        assert "<Response>" in xml
        assert "<Connect>" in xml
        assert "wss://abc.ngrok.app/ws" in xml
        assert 'name="to_number"' in xml and "+15555551234" in xml
        assert 'name="from_number"' in xml and "+15555550123" in xml
        assert 'name="agent_id"' in xml and 'value="7"' in xml
        assert 'name="user_id"' in xml and 'value="1"' in xml
        assert 'name="target_name"' in xml and 'value="Mom"' in xml
        assert "<Pause" in xml
