"""Integration tests for the `Contacts` model against a real in-memory SQLite DB."""

import base64
from datetime import datetime

import pytest

from app.models.contacts import Contacts
from app.models.users import Users


def _make_user(test_db, *, username="alice") -> Users:
    user = Users(username=username, hashed_password="pw")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.mark.integration
class TestContactsModel:
    def test_insert_contact_sets_defaults(self, test_db):
        owner = _make_user(test_db)

        contact = Contacts(
            owner_id=owner.id,
            name="Bob",
            phone_number="+15555551234",
            image_filename="bob.png",
            image_data=b"\x89PNG",
        )
        test_db.add(contact)
        test_db.commit()
        test_db.refresh(contact)

        assert contact.id is not None
        assert contact.owner_id == owner.id
        assert isinstance(contact.created_at, datetime)

    def test_image_property_returns_base64(self, test_db):
        owner = _make_user(test_db)
        raw = b"\x89PNG-bytes"

        contact = Contacts(
            owner_id=owner.id,
            name="Bob",
            phone_number="+15555551234",
            image_filename="bob.png",
            image_data=raw,
        )
        test_db.add(contact)
        test_db.commit()
        test_db.refresh(contact)

        assert contact.image == base64.b64encode(raw).decode()

    def test_image_property_is_none_when_no_image_data(self, test_db):
        owner = _make_user(test_db)

        contact = Contacts(
            owner_id=owner.id,
            name="Bob",
            phone_number="+15555551234",
            image_filename=None,
            image_data=None,
        )
        test_db.add(contact)
        test_db.commit()
        test_db.refresh(contact)

        assert contact.image is None

    def test_multiple_contacts_per_owner(self, test_db):
        owner = _make_user(test_db)
        for name in ["Bob", "Alice", "Charlie"]:
            test_db.add(
                Contacts(
                    owner_id=owner.id,
                    name=name,
                    phone_number="+15555550000",
                    image_filename=None,
                    image_data=None,
                )
            )
        test_db.commit()

        contacts = test_db.query(Contacts).filter(Contacts.owner_id == owner.id).all()
        assert {c.name for c in contacts} == {"Bob", "Alice", "Charlie"}

    def test_delete_contact(self, test_db):
        owner = _make_user(test_db)
        contact = Contacts(
            owner_id=owner.id,
            name="Bob",
            phone_number="+15555551234",
            image_filename=None,
            image_data=None,
        )
        test_db.add(contact)
        test_db.commit()
        contact_id = contact.id

        test_db.delete(contact)
        test_db.commit()

        assert test_db.query(Contacts).filter(Contacts.id == contact_id).first() is None

    def test_filter_by_owner_isolates_contacts(self, test_db):
        alice = _make_user(test_db, username="alice")
        bob = _make_user(test_db, username="bob")

        test_db.add(
            Contacts(
                owner_id=alice.id,
                name="AliceContact",
                phone_number="+1",
                image_filename=None,
                image_data=None,
            )
        )
        test_db.add(
            Contacts(
                owner_id=bob.id,
                name="BobContact",
                phone_number="+2",
                image_filename=None,
                image_data=None,
            )
        )
        test_db.commit()

        alice_contacts = (
            test_db.query(Contacts).filter(Contacts.owner_id == alice.id).all()
        )
        bob_contacts = (
            test_db.query(Contacts).filter(Contacts.owner_id == bob.id).all()
        )

        assert len(alice_contacts) == 1 and alice_contacts[0].name == "AliceContact"
        assert len(bob_contacts) == 1 and bob_contacts[0].name == "BobContact"
