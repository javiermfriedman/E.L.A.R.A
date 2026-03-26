
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from starlette import status

from app.dependencies import db_dependency, user_dependency
from app.models.contacts import Contacts
from app.schemas.contacts import ContactResponse
from loguru import logger

from app.services.image_preprocess import crop_and_resize

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"],
)

ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/webp"}


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ContactResponse)
async def add_contact(
    db: db_dependency,
    user: user_dependency,
    name: str = Form(...),
    phone_number: str = Form(...),
    image: UploadFile = File(...),
):
    logger.info(f"Adding contact: name={name}")

    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Image must be PNG, JPEG, or WebP")

    image_bytes = await image.read()
    image_bytes = crop_and_resize(image_bytes)

    contact_model = Contacts(
        name=name,
        phone_number=phone_number,
        image_data=image_bytes,
        image_filename=image.filename,
        owner_id=user["id"],
    )
    logger.info(f"Contact model: {contact_model}")
    db.add(contact_model)
    db.commit()
    db.refresh(contact_model)
    logger.info(f"Contact added: {contact_model}")
    return contact_model


@router.get("/", response_model=list[ContactResponse])
async def get_contacts(db: db_dependency, user: user_dependency):
    contacts = db.query(Contacts).filter(Contacts.owner_id == user["id"]).all()
    return contacts
