"""
validators.py — Input validation for CLI arguments.

All validation errors are raised as ValueError with a human-readable message.
"""

import re
from config import VALID_SIDES, VALID_ORDER_TYPES


def validate_symbol(symbol: str) -> str:
    """Symbol must be uppercase alphanumeric (e.g. BTCUSDT)."""
    symbol = symbol.upper().strip()
    if not re.fullmatch(r"[A-Z0-9]+", symbol):
        raise ValueError(f"Invalid symbol '{symbol}'. Must be uppercase alphanumeric (e.g. BTCUSDT).")
    return symbol


def validate_side(side: str) -> str:
    """Side must be BUY or SELL."""
    side = side.upper().strip()
    if side not in VALID_SIDES:
        raise ValueError(f"Invalid side '{side}'. Must be one of {VALID_SIDES}.")
    return side


def validate_order_type(order_type: str) -> str:
    """Order type must be MARKET, LIMIT, or STOP_LIMIT."""
    order_type = order_type.upper().strip()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(f"Invalid order type '{order_type}'. Must be one of {VALID_ORDER_TYPES}.")
    return order_type


def validate_quantity(quantity: float) -> float:
    """Quantity must be a positive number."""
    if quantity is None or quantity <= 0:
        raise ValueError(f"Quantity must be a positive number, got {quantity}.")
    return quantity


def validate_price(price: float | None, order_type: str) -> float | None:
    """Price is required (and must be positive) for LIMIT and STOP_LIMIT orders."""
    if order_type in ("LIMIT", "STOP_LIMIT"):
        if price is None or price <= 0:
            raise ValueError(f"Price is required and must be positive for {order_type} orders.")
    return price


def validate_stop_price(stop_price: float | None, order_type: str) -> float | None:
    """Stop price is required (and must be positive) for STOP_LIMIT orders."""
    if order_type == "STOP_LIMIT":
        if stop_price is None or stop_price <= 0:
            raise ValueError("Stop price is required and must be positive for STOP_LIMIT orders.")
    return stop_price


def validate_tp_sl(
    take_profit: float | None,
    stop_loss: float | None,
    side: str,
) -> tuple[float | None, float | None]:
    """Validate Take-Profit and Stop-Loss prices if provided."""
    if take_profit is not None:
        if take_profit <= 0:
            raise ValueError("Take-profit price must be a positive number.")
    if stop_loss is not None:
        if stop_loss <= 0:
            raise ValueError("Stop-loss price must be a positive number.")

    # Sanity check: TP above entry for BUY, below for SELL (and inverse for SL)
    if take_profit and stop_loss:
        if side == "BUY" and stop_loss >= take_profit:
            raise ValueError("For BUY orders, stop-loss must be below take-profit.")
        if side == "SELL" and stop_loss <= take_profit:
            raise ValueError("For SELL orders, stop-loss must be above take-profit.")

    return take_profit, stop_loss


def validate_order_params(args) -> dict:
    """
    Run all validations on the parsed CLI arguments. Returns a clean dict.

    Raises ValueError on the first validation failure.
    """
    symbol = validate_symbol(args.symbol)
    side = validate_side(args.side)
    order_type = validate_order_type(args.type)
    quantity = validate_quantity(args.quantity)
    price = validate_price(args.price, order_type)
    stop_price = validate_stop_price(getattr(args, "stop_price", None), order_type)
    take_profit, stop_loss = validate_tp_sl(
        getattr(args, "tp", None),
        getattr(args, "sl", None),
        side,
    )

    return {
        "symbol": symbol,
        "side": side,
        "order_type": order_type,
        "quantity": quantity,
        "price": price,
        "stop_price": stop_price,
        "take_profit": take_profit,
        "stop_loss": stop_loss,
    }
