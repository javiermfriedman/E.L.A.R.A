"""Integration tests for the `Users` model against a real in-memory SQLite DB."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.users import Users


@pytest.mark.integration
class TestUsersModel:
    def test_insert_and_query_user(self, test_db):
        user = Users(username="alice", hashed_password="hashed-pw")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.id is not None

        fetched = test_db.query(Users).filter(Users.username == "alice").first()
        assert fetched is not None
        assert fetched.id == user.id
        assert fetched.hashed_password == "hashed-pw"

    def test_username_is_unique(self, test_db):
        test_db.add(Users(username="alice", hashed_password="pw-1"))
        test_db.commit()

        test_db.add(Users(username="alice", hashed_password="pw-2"))
        with pytest.raises(IntegrityError):
            test_db.commit()
        test_db.rollback()

    def test_delete_user(self, test_db):
        user = Users(username="alice", hashed_password="pw")
        test_db.add(user)
        test_db.commit()

        test_db.delete(user)
        test_db.commit()

        assert test_db.query(Users).filter(Users.username == "alice").first() is None

    def test_query_nonexistent_user_returns_none(self, test_db):
        assert test_db.query(Users).filter(Users.username == "ghost").first() is None
