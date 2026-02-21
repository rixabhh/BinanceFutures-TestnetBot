"""
orders.py — Order execution logic for Binance Futures Testnet.

Maps validated parameters to the correct python-binance API call
and logs every request/response cycle.
"""

import json
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from logging_config import setup_logging

logger = setup_logging()


def place_market_order(client: Client, symbol: str, side: str, quantity: float) -> dict:
    """Place a MARKET order on Binance Futures Testnet."""
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
    }
    logger.info("Placing MARKET order  →  %s", json.dumps(params))

    response = client.futures_create_order(**params)
    logger.info("MARKET order response  →  %s", json.dumps(response, indent=2))
    return response


def place_limit_order(
    client: Client, symbol: str, side: str, quantity: float, price: float
) -> dict:
    """Place a LIMIT order (GTC) on Binance Futures Testnet."""
    params = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": quantity,
        "price": price,
    }
    logger.info("Placing LIMIT order  →  %s", json.dumps(params))

    response = client.futures_create_order(**params)
    logger.info("LIMIT order response  →  %s", json.dumps(response, indent=2))
    return response


def place_stop_limit_order(
    client: Client,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    stop_price: float,
) -> dict:
    """Place a STOP-LIMIT order on Binance Futures Testnet."""
    params = {
        "symbol": symbol,
        "side": side,
        "type": "STOP",
        "timeInForce": "GTC",
        "quantity": quantity,
        "price": price,
        "stopPrice": stop_price,
    }
    logger.info("Placing STOP-LIMIT order  →  %s", json.dumps(params))

    response = client.futures_create_order(**params)
    logger.info("STOP-LIMIT order response  →  %s", json.dumps(response, indent=2))
    return response


def place_order(client: Client, params: dict) -> dict:
    """
    Dispatcher — routes to the correct order function based on order_type.

    Args:
        client:  Authenticated Binance Client.
        params:  Validated dict with keys: symbol, side, order_type, quantity,
                 price (optional), stop_price (optional).

    Returns:
        Raw API response dict.

    Raises:
        BinanceAPIException / BinanceRequestException on API errors.
    """
    order_type = params["order_type"]

    try:
        if order_type == "MARKET":
            return place_market_order(
                client, params["symbol"], params["side"], params["quantity"]
            )
        elif order_type == "LIMIT":
            return place_limit_order(
                client,
                params["symbol"],
                params["side"],
                params["quantity"],
                params["price"],
            )
        elif order_type == "STOP_LIMIT":
            return place_stop_limit_order(
                client,
                params["symbol"],
                params["side"],
                params["quantity"],
                params["price"],
                params["stop_price"],
            )
        else:
            raise ValueError(f"Unsupported order type: {order_type}")

    except BinanceAPIException as exc:
        logger.error("Binance API error [%s]: %s", exc.status_code, exc.message)
        raise
    except BinanceRequestException as exc:
        logger.error("Binance request error: %s", exc)
        raise
    except Exception as exc:
        logger.exception("Unexpected error placing order: %s", exc)
        raise


# ── Take-Profit & Stop-Loss ──────────────────────────────────────────────────

def _opposite_side(side: str) -> str:
    """Return the opposite side (used to close a position)."""
    return "SELL" if side == "BUY" else "BUY"


def place_take_profit(
    client: Client, symbol: str, side: str, quantity: float, tp_price: float
) -> dict:
    """Place a TAKE_PROFIT_MARKET order to auto-close at the target price."""
    close_side = _opposite_side(side)
    params = {
        "symbol": symbol,
        "side": close_side,
        "type": "TAKE_PROFIT_MARKET",
        "quantity": quantity,
        "stopPrice": tp_price,
    }
    logger.info("Placing TAKE-PROFIT  →  %s", json.dumps(params))
    response = client.futures_create_order(**params)
    logger.info("TAKE-PROFIT response  →  %s", json.dumps(response, indent=2))
    return response


def place_stop_loss(
    client: Client, symbol: str, side: str, quantity: float, sl_price: float
) -> dict:
    """Place a STOP_MARKET order to auto-close at the stop-loss price."""
    close_side = _opposite_side(side)
    params = {
        "symbol": symbol,
        "side": close_side,
        "type": "STOP_MARKET",
        "quantity": quantity,
        "stopPrice": sl_price,
    }
    logger.info("Placing STOP-LOSS  →  %s", json.dumps(params))
    response = client.futures_create_order(**params)
    logger.info("STOP-LOSS response  →  %s", json.dumps(response, indent=2))
    return response


def attach_tp_sl(client: Client, params: dict) -> dict:
    """
    After the primary order, attach TP and/or SL orders.

    Returns a dict with 'take_profit' and 'stop_loss' responses (or None).
    """
    results = {"take_profit": None, "stop_loss": None}
    symbol = params["symbol"]
    side = params["side"]
    quantity = params["quantity"]

    try:
        if params.get("take_profit"):
            results["take_profit"] = place_take_profit(
                client, symbol, side, quantity, params["take_profit"]
            )
        if params.get("stop_loss"):
            results["stop_loss"] = place_stop_loss(
                client, symbol, side, quantity, params["stop_loss"]
            )
    except BinanceAPIException as exc:
        logger.error("TP/SL API error [%s]: %s", exc.status_code, exc.message)
        raise
    except Exception as exc:
        logger.exception("TP/SL unexpected error: %s", exc)
        raise

    return results
