from fastapi import FastAPI
import app.models.users  # noqa: F401 — register models with Base
import app.models.recordings  # noqa: F401
from app.database import engine, Base
from app.routers import auth, agents, contacts, calls, recordings
import logging
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),          # print to terminal
        logging.FileHandler("app.log"),   # save to file
    ],
)

logger = logging.getLogger(__name__)
app = FastAPI()

logger.info("Starting Prank Caller API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Creating all tables in the database")

# create all tables in the database
Base.metadata.create_all(bind=engine)
logger.info("All tables created")

# include routers
app.include_router(auth.router)
app.include_router(agents.router)
app.include_router(contacts.router)
app.include_router(calls.router)
app.include_router(recordings.router)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
