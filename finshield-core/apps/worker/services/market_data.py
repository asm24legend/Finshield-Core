import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"


def get_company_overview(symbol: str) -> dict | None:
    """
    Fetches key financial metrics for a public company via Alpha Vantage's
    OVERVIEW endpoint (free tier). Returns None if the symbol isn't found
    or the API rate limit is hit (free tier: 25 requests/day, 5/minute).
    """
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": API_KEY,
    }
    response = requests.get(BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    if not data or "Symbol" not in data:
        return None  # symbol not found, or rate-limited

    return {
        "symbol": data.get("Symbol"),
        "name": data.get("Name"),
        "sector": data.get("Sector"),
        "market_cap": data.get("MarketCapitalization"),
        "pe_ratio": data.get("PERatio"),
        "beta": data.get("Beta"),
        "profit_margin": data.get("ProfitMargin"),
    }