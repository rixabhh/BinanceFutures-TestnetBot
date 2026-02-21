"""
config.py — Centralized configuration for the Binance Futures Testnet bot.

Loads API credentials from a .env file and defines application-wide constants.
"""

import os
import sys
from dotenv import load_dotenv

# ── Load .env ────────────────────────────────────────────────────────────────
load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

if not API_KEY or not API_SECRET:
    print("[ERROR] BINANCE_API_KEY and BINANCE_API_SECRET must be set in .env")
    sys.exit(1)

# ── Testnet settings ─────────────────────────────────────────────────────────
TESTNET_BASE_URL = "https://testnet.binancefuture.com"

# ── Allowed values ────────────────────────────────────────────────────────────
VALID_SIDES = ("BUY", "SELL")
VALID_ORDER_TYPES = ("MARKET", "LIMIT", "STOP_LIMIT")
