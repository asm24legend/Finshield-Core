import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Dynamically find the directory where THIS config.py file lives
current_dir = Path(__file__).resolve().parent

# 2. Look explicitly for a file named '.env' in this exact directory
env_path = current_dir / ".env"

# 3. Tell python-dotenv exactly where to look
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        f"DATABASE_URL is not set. Looked for a .env file at: {env_path}\n"
        f"Please ensure a valid .env file exists in that exact location."
    )