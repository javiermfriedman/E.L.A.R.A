"""Integration tests for the `Agents` model against a real in-memory SQLite DB."""

import base64
from datetime import datetime

import pytest

from app.models.agents import Agents
from app.models.users import Users


def _make_user(test_db, *, username="alice") -> Users:
    user = Users(username=username, hashed_password="pw")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.mark.integration
class TestAgentsModel:
    def test_insert_agent_sets_defaults(self, test_db):
        owner = _make_user(test_db)

        agent = Agents(
            owner_id=owner.id,
            voice_id="v1",
            name="Zeus",
            description="desc",
            system_prompt="sp",
            first_message="hi",
            image_filename="zeus.png",
            image_data=b"\x89PNGfake",
        )
        test_db.add(agent)
        test_db.commit()
        test_db.refresh(agent)

        assert agent.id is not None
        assert agent.owner_id == owner.id
        assert isinstance(agent.created_at, datetime)

    def test_image_property_returns_base64(self, test_db):
        owner = _make_user(test_db)

        raw = b"\x89PNGfake-bytes"
        agent = Agents(
            owner_id=owner.id,
            voice_id="v1",
            name="Zeus",
            description="d",
            system_prompt="sp",
            first_message="hi",
            image_filename="zeus.png",
            image_data=raw,
        )
        test_db.add(agent)
        test_db.commit()
        test_db.refresh(agent)

        assert agent.image == base64.b64encode(raw).decode()

    def test_image_property_is_none_when_no_image_data(self, test_db):
        owner = _make_user(test_db)

        agent = Agents(
            owner_id=owner.id,
            voice_id="v1",
            name="Zeus",
            description="d",
            system_prompt="sp",
            first_message="hi",
            image_filename=None,
            image_data=None,
        )
        test_db.add(agent)
        test_db.commit()
        test_db.refresh(agent)

        assert agent.image is None

    def test_multiple_agents_per_owner(self, test_db):
        owner = _make_user(test_db)

        for name in ["Zeus", "Hera", "Apollo"]:
            test_db.add(
                Agents(
                    owner_id=owner.id,
                    voice_id="v1",
                    name=name,
                    description="d",
                    system_prompt="sp",
                    first_message="hi",
                    image_filename=f"{name.lower()}.png",
                    image_data=b"\x89PNG",
                )
            )
        test_db.commit()

        agents = test_db.query(Agents).filter(Agents.owner_id == owner.id).all()
        assert {a.name for a in agents} == {"Zeus", "Hera", "Apollo"}

    def test_delete_agent(self, test_db):
        owner = _make_user(test_db)
        agent = Agents(
            owner_id=owner.id,
            voice_id="v1",
            name="Zeus",
            description="d",
            system_prompt="sp",
            first_message="hi",
            image_filename="z.png",
            image_data=b"\x89PNG",
        )
        test_db.add(agent)
        test_db.commit()
        agent_id = agent.id

        test_db.delete(agent)
        test_db.commit()

        assert test_db.query(Agents).filter(Agents.id == agent_id).first() is None

    def test_filter_by_owner_isolates_agents(self, test_db):
        alice = _make_user(test_db, username="alice")
        bob = _make_user(test_db, username="bob")

        test_db.add(
            Agents(
                owner_id=alice.id,
                voice_id="v",
                name="AliceBot",
                description="",
                system_prompt="",
                first_message="",
                image_filename="",
                image_data=b"",
            )
        )
        test_db.add(
            Agents(
                owner_id=bob.id,
                voice_id="v",
                name="BobBot",
                description="",
                system_prompt="",
                first_message="",
                image_filename="",
                image_data=b"",
            )
        )
        test_db.commit()

        alice_agents = test_db.query(Agents).filter(Agents.owner_id == alice.id).all()
        bob_agents = test_db.query(Agents).filter(Agents.owner_id == bob.id).all()

        assert len(alice_agents) == 1 and alice_agents[0].name == "AliceBot"
        assert len(bob_agents) == 1 and bob_agents[0].name == "BobBot"
