from io import BytesIO

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from PIL import Image
from starlette import status

from app.dependencies import db_dependency, user_dependency
from app.models.agents import Agents
from app.schemas.agents import AgentResponse
from loguru import logger

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
)

ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/webp"}
AVATAR_SIZE = 256  # all agent images are stored as 256×256 PNG

# expects a png or jpg image file
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AgentResponse)
async def add_agent(
    db: db_dependency,
    user: user_dependency,
    name: str = Form(...),
    description: str = Form(...),
    system_prompt: str = Form(...),
    voice_id: str = Form("zmcVlqmyk3Jpn5AVYcAL"),
    image: UploadFile = File(...),
):
    logger.info(f"Adding agent: name={name}")

    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Image must be PNG, JPEG, or WebP")

    image_bytes = await image.read()

    image_bytes = crop_and_resize(image_bytes)

    agent_model = Agents(
        name=name,
        description=description,
        system_prompt=system_prompt,
        voice_id=voice_id,
        image_data=image_bytes,
        image_filename=image.filename,
        owner_id=user["id"],
    )
    logger.info(f"Agent model: {agent_model}")
    db.add(agent_model)
    db.commit()
    db.refresh(agent_model)
    logger.info(f"Agent added: {agent_model}")
    return agent_model

@router.get("/", response_model=list[AgentResponse])
async def get_agents(db: db_dependency, user: user_dependency):
    agents = db.query(Agents).filter(Agents.owner_id == user["id"]).all()
    return agents



def crop_and_resize(raw_bytes: bytes) -> bytes:
    """Center-crop to a square, resize to AVATAR_SIZE×AVATAR_SIZE, return PNG bytes."""
    img = Image.open(BytesIO(raw_bytes))
    img = img.convert("RGBA")

    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    img = img.resize((AVATAR_SIZE, AVATAR_SIZE), Image.LANCZOS)

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()