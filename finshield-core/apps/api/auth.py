import os
import secrets
import config  # noqa: F401  (importing it runs load_dotenv, so API_KEY is in the environment)
from fastapi import Header, HTTPException


def require_api_key(x_api_key: str | None = Header(default=None)):
    expected = os.getenv("API_KEY")
    if not expected:
        # Fail closed: a missing server key must never mean "open to everyone".
        raise HTTPException(status_code=503, detail="Server API key not configured")
    # compare_digest avoids leaking information through comparison timing
    if not x_api_key or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")