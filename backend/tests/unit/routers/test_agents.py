"""Unit tests for the `agents` router."""

from datetime import datetime
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest


def _make_agent_row(
    *,
    id: int = 1,
    owner_id: int = 1,
    name: str = "Zeus",
    description: str = "King of gods",
    system_prompt: str = "You are Zeus.",
    first_message: str = "Hello mortal.",
    voice_id: str = "zmcVlqmyk3Jpn5AVYcAL",
    image_data: bytes = b"\x89PNGfake",
    image_filename: str = "zeus.png",
    created_at: datetime | None = None,
) -> MagicMock:
    """Build a MagicMock that quacks like an `Agents` ORM row."""
    agent = MagicMock()
    agent.id = id
    agent.owner_id = owner_id
    agent.name = name
    agent.description = description
    agent.system_prompt = system_prompt
    agent.first_message = first_message
    agent.voice_id = voice_id
    agent.image_data = image_data
    agent.image_filename = image_filename
    agent.created_at = created_at or datetime(2026, 1, 1, 12, 0, 0)
    # Mirror the `image` @property on the real model.
    import base64
    agent.image = base64.b64encode(image_data).decode()
    return agent


@pytest.mark.unit
class TestAddAgent:
    def test_add_agent_success(self, client, mock_db):
        created = _make_agent_row()

        def _refresh(instance):
            instance.id = created.id
            instance.created_at = created.created_at
            instance.image_data = b"resized-bytes"

        mock_db.refresh.side_effect = _refresh

        with patch(
            "app.routers.agents.crop_and_resize", return_value=b"resized-bytes"
        ) as mock_crop:
            resp = client.post(
                "/agents/",
                data={
                    "name": "Zeus",
                    "description": "King of gods",
                    "system_prompt": "You are Zeus.",
                    "first_message": "Hello mortal.",
                    "voice_id": "zmcVlqmyk3Jpn5AVYcAL",
                },
                files={"image": ("zeus.png", BytesIO(b"rawbytes"), "image/png")},
            )

        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "Zeus"
        assert body["description"] == "King of gods"
        mock_crop.assert_called_once_with(b"rawbytes")
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

        added = mock_db.add.call_args.args[0]
        assert added.name == "Zeus"
        assert added.owner_id == 1  # from mock_user fixture
        assert added.image_data == b"resized-bytes"

    def test_add_agent_rejects_unsupported_content_type(self, client):
        resp = client.post(
            "/agents/",
            data={
                "name": "Zeus",
                "description": "desc",
                "system_prompt": "sp",
                "first_message": "hi",
            },
            files={"image": ("zeus.gif", BytesIO(b"rawbytes"), "image/gif")},
        )
        assert resp.status_code == 400
        assert "PNG" in resp.json()["detail"]

    def test_add_agent_missing_fields_returns_422(self, client):
        resp = client.post(
            "/agents/",
            data={"name": "Zeus"},
            files={"image": ("zeus.png", BytesIO(b"x"), "image/png")},
        )
        assert resp.status_code == 422


@pytest.mark.unit
class TestGetAgents:
    def test_get_agents_returns_list(self, client, mock_db):
        agents = [_make_agent_row(id=1), _make_agent_row(id=2, name="Hera")]
        mock_db.query.return_value.filter.return_value.all.return_value = agents

        resp = client.get("/agents/")

        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 2
        assert body[0]["id"] == 1
        assert body[1]["name"] == "Hera"

    def test_get_agents_empty(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.all.return_value = []
        resp = client.get("/agents/")
        assert resp.status_code == 200
        assert resp.json() == []


@pytest.mark.unit
class TestDeleteAllAgents:
    def test_delete_all_agents(self, client, mock_db):
        agents = [_make_agent_row(id=1), _make_agent_row(id=2)]
        mock_db.query.return_value.filter.return_value.all.return_value = agents

        resp = client.delete("/agents/")

        assert resp.status_code == 200
        assert resp.json() == {"message": "Agents deleted successfully"}
        assert mock_db.delete.call_count == 2
        mock_db.commit.assert_called_once()


@pytest.mark.unit
class TestDeleteAgentById:
    def test_delete_agent_success(self, client, mock_db):
        agent = _make_agent_row(id=7)
        mock_db.query.return_value.filter.return_value.first.return_value = agent

        resp = client.delete("/agents/7")

        assert resp.status_code == 200
        assert "7" in resp.json()["message"]
        mock_db.delete.assert_called_once_with(agent)
        mock_db.commit.assert_called_once()

    def test_delete_agent_not_found(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        resp = client.delete("/agents/999")

        assert resp.status_code == 404
        assert resp.json()["detail"] == "Agent not found"
        mock_db.delete.assert_not_called()
