"""Unit tests for the `auth` router.

External dependencies (bcrypt, jwt, DB) are mocked. These tests verify the
routing/wiring logic of endpoints, not the real hashing/token behavior.
"""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError


@pytest.mark.unit
class TestCreateUser:
    def test_create_user_success(self, client, mock_db):
        with patch("app.routers.auth.bcrypt_context") as mock_bcrypt:
            mock_bcrypt.hash.return_value = "hashed-pw"

            resp = client.post(
                "/auth/",
                json={"username": "alice", "password": "supersecret"},
            )

        assert resp.status_code == 201
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

        added = mock_db.add.call_args.args[0]
        assert added.username == "alice"
        assert added.hashed_password == "hashed-pw"

    def test_create_user_duplicate_username_returns_409(self, client, mock_db):
        mock_db.commit.side_effect = IntegrityError("stmt", {}, Exception("dup"))

        with patch("app.routers.auth.bcrypt_context") as mock_bcrypt:
            mock_bcrypt.hash.return_value = "hashed-pw"

            resp = client.post(
                "/auth/",
                json={"username": "alice", "password": "supersecret"},
            )

        assert resp.status_code == 409
        assert resp.json()["detail"] == "Username already registered"
        mock_db.rollback.assert_called_once()

    def test_create_user_missing_fields_returns_422(self, client):
        resp = client.post("/auth/", json={"username": "alice"})
        assert resp.status_code == 422


@pytest.mark.unit
class TestLoginForAccessToken:
    def test_login_success_returns_token(self, client, mock_db):
        fake_user = MagicMock(id=42, username="alice", hashed_password="hashed-pw")

        with (
            patch("app.routers.auth.authenticate_user", return_value=fake_user) as m_auth,
            patch("app.routers.auth.create_access_token", return_value="jwt-token") as m_token,
        ):
            resp = client.post(
                "/auth/token",
                data={"username": "alice", "password": "supersecret"},
            )

        assert resp.status_code == 200
        assert resp.json() == {"access_token": "jwt-token", "token_type": "bearer"}
        m_auth.assert_called_once_with("alice", "supersecret", mock_db)
        m_token.assert_called_once()

    def test_login_bad_credentials_returns_401(self, client):
        with patch("app.routers.auth.authenticate_user", return_value=False):
            resp = client.post(
                "/auth/token",
                data={"username": "alice", "password": "wrong"},
            )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Could not validate credentials"


@pytest.mark.unit
class TestAuthenticateUserHelper:
    def test_authenticate_user_returns_user_on_valid_password(self):
        from app.routers.auth import authenticate_user

        fake_user = MagicMock(username="alice", hashed_password="hashed-pw")
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = fake_user

        with patch("app.routers.auth.bcrypt_context") as mock_bcrypt:
            mock_bcrypt.verify.return_value = True
            result = authenticate_user("alice", "supersecret", db)

        assert result is fake_user
        mock_bcrypt.verify.assert_called_once_with("supersecret", "hashed-pw")

    def test_authenticate_user_returns_false_when_user_missing(self):
        from app.routers.auth import authenticate_user

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        assert authenticate_user("ghost", "pw", db) is False

    def test_authenticate_user_returns_false_on_bad_password(self):
        from app.routers.auth import authenticate_user

        fake_user = MagicMock(hashed_password="hashed-pw")
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = fake_user

        with patch("app.routers.auth.bcrypt_context") as mock_bcrypt:
            mock_bcrypt.verify.return_value = False
            assert authenticate_user("alice", "wrong", db) is False


@pytest.mark.unit
class TestCreateAccessToken:
    def test_create_access_token_encodes_expected_payload(self):
        from datetime import timedelta

        from app.routers.auth import create_access_token

        with patch("app.routers.auth.jwt") as mock_jwt:
            mock_jwt.encode.return_value = "signed-token"
            token = create_access_token("alice", 42, timedelta(minutes=20))

        assert token == "signed-token"
        payload = mock_jwt.encode.call_args.args[0]
        assert payload["sub"] == "alice"
        assert payload["id"] == 42
        assert "exp" in payload
