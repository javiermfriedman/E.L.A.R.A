"""Unit tests for `app.dependencies.get_current_user` (JWT decoding)."""

from unittest.mock import patch

import pytest
from fastapi import HTTPException
from jose import JWTError


@pytest.mark.unit
class TestGetCurrentUser:
    async def test_valid_token_returns_user_dict(self):
        from app.dependencies import get_current_user

        with patch("app.dependencies.jwt") as mock_jwt:
            mock_jwt.decode.return_value = {"sub": "alice", "id": 42}
            result = await get_current_user("valid-token")
        assert result == {"username": "alice", "id": 42}

    async def test_missing_sub_raises_401(self):
        from app.dependencies import get_current_user

        with patch("app.dependencies.jwt") as mock_jwt:
            mock_jwt.decode.return_value = {"id": 42}  # no sub
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("valid-token")
        assert exc_info.value.status_code == 401

    async def test_missing_id_raises_401(self):
        from app.dependencies import get_current_user

        with patch("app.dependencies.jwt") as mock_jwt:
            mock_jwt.decode.return_value = {"sub": "alice"}  # no id
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("valid-token")
        assert exc_info.value.status_code == 401

    async def test_bad_jwt_raises_401(self):
        from app.dependencies import get_current_user

        with patch("app.dependencies.jwt") as mock_jwt:
            mock_jwt.decode.side_effect = JWTError("invalid")
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("bad-token")
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Could not validate credentials"
