import uvicorn
import os
import sys
from dotenv import load_dotenv

# Load env vars from .env file
load_dotenv()

# Ensure the current directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.db import init_db

# Initialize setup
init_db()

if __name__ == "__main__":
    # wrapper to run the app with reload enabled
    # "backend.api:app" string is required for reload to work
    uvicorn.run("backend.api:app", host="0.0.0.0", port=8000, reload=True)
