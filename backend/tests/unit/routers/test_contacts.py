"""Unit tests for the `contacts` router."""

from datetime import datetime
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest


def _make_contact_row(
    *,
    id: int = 1,
    owner_id: int = 1,
    name: str = "Bob",
    phone_number: str = "+15555551234",
    image_data: bytes = b"\x89PNGfake",
    image_filename: str = "bob.png",
    created_at: datetime | None = None,
) -> MagicMock:
    contact = MagicMock()
    contact.id = id
    contact.owner_id = owner_id
    contact.name = name
    contact.phone_number = phone_number
    contact.image_data = image_data
    contact.image_filename = image_filename
    contact.created_at = created_at or datetime(2026, 1, 1, 12, 0, 0)
    import base64
    contact.image = base64.b64encode(image_data).decode()
    return contact


@pytest.mark.unit
class TestAddContact:
    def test_add_contact_success(self, client, mock_db):
        def _refresh(instance):
            instance.id = 1
            instance.created_at = datetime(2026, 1, 1, 12, 0, 0)
            instance.image_data = b"resized-bytes"

        mock_db.refresh.side_effect = _refresh

        with patch(
            "app.routers.contacts.crop_and_resize", return_value=b"resized-bytes"
        ) as mock_crop:
            resp = client.post(
                "/contacts/",
                data={"name": "Bob", "phone_number": "+15555551234"},
                files={"image": ("bob.jpg", BytesIO(b"rawbytes"), "image/jpeg")},
            )

        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "Bob"
        assert body["phone_number"] == "+15555551234"
        mock_crop.assert_called_once_with(b"rawbytes")
        mock_db.add.assert_called_once()
        added = mock_db.add.call_args.args[0]
        assert added.owner_id == 1
        assert added.image_data == b"resized-bytes"

    def test_add_contact_rejects_bad_image_type(self, client):
        resp = client.post(
            "/contacts/",
            data={"name": "Bob", "phone_number": "+15555551234"},
            files={"image": ("bob.bmp", BytesIO(b"x"), "image/bmp")},
        )
        assert resp.status_code == 400

    def test_add_contact_missing_phone_returns_422(self, client):
        resp = client.post(
            "/contacts/",
            data={"name": "Bob"},
            files={"image": ("bob.png", BytesIO(b"x"), "image/png")},
        )
        assert resp.status_code == 422


@pytest.mark.unit
class TestGetContacts:
    def test_get_contacts_returns_list(self, client, mock_db):
        contacts = [_make_contact_row(id=1), _make_contact_row(id=2, name="Alice")]
        mock_db.query.return_value.filter.return_value.all.return_value = contacts

        resp = client.get("/contacts/")

        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 2
        assert body[0]["name"] == "Bob"
        assert body[1]["name"] == "Alice"


@pytest.mark.unit
class TestDeleteContacts:
    def test_delete_all_contacts(self, client, mock_db):
        contacts = [_make_contact_row(id=1), _make_contact_row(id=2)]
        mock_db.query.return_value.filter.return_value.all.return_value = contacts

        resp = client.delete("/contacts/")

        assert resp.status_code == 200
        assert resp.json() == {"message": "Contacts deleted successfully"}
        assert mock_db.delete.call_count == 2
        mock_db.commit.assert_called_once()
