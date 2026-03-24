from fastapi import APIRouter, HTTPException
from starlette import status

from app.dependencies import db_dependency, user_dependency
from app.models.contacts import Contacts
from app.schemas.contacts import ContactCreate, ContactResponse
from loguru import logger

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"],
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ContactResponse)
async def add_contact(contact: ContactCreate, db: db_dependency, user: user_dependency):
    logger.info(f"Adding contact: {contact}")
    contact_model = Contacts(
        name=contact.name,
        phone_number=contact.phone_number,
        owner_id=user["id"],  # comes from the JWT token, not from the request
    )
    logger.info(f"Contact model: {contact_model}")
    db.add(contact_model)
    db.commit()
    db.refresh(contact_model)
    logger.info(f"Contact added: {contact_model}")
    return contact_model

@router.get("/", response_model=list[ContactResponse])
async def get_contacts(db: db_dependency, user: user_dependency):
    # only return groceries belonging to the logged-in user
    contacts = db.query(Contacts).filter(Contacts.owner_id == user["id"]).all()
    return contacts
