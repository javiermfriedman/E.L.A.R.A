import os
from dotenv import load_dotenv

# Load .env file from the backend directory
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SECRET_KEY = "ySRJENALSFNWDSFAEEDSFXFAFEEFS"
ALGORITHM = "HS256"  # STANDARD ALGORITHM FOR JWT
