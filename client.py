"""
client.py — Binance Futures Testnet client factory.

Creates an authenticated python-binance Client pointing at the Futures Testnet.
"""

from binance.client import Client
from config import API_KEY, API_SECRET, TESTNET_BASE_URL
from logging_config import setup_logging

logger = setup_logging()


def get_client() -> Client:
    """
    Create and return a Binance Client configured for Futures Testnet.

    The client is set to testnet mode so all requests hit the sandbox
    environment instead of the live exchange.
    """
    logger.info("Initializing Binance Futures Testnet client …")
    try:
        client = Client(API_KEY, API_SECRET, testnet=True)
        # Override the futures base URL to the official testnet endpoint
        client.FUTURES_URL = TESTNET_BASE_URL + "/fapi"
        logger.info("Client ready  →  %s", TESTNET_BASE_URL)
        return client
    except Exception as exc:
        logger.exception("Failed to create Binance client: %s", exc)
        raise
