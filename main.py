"""
main.py -- CLI entry-point for the Binance Futures Testnet trading bot.

Usage examples:
    python main.py BTCUSDT BUY MARKET 0.002
    python main.py ETHUSDT SELL LIMIT 0.05 --price 3200
    python main.py BTCUSDT BUY MARKET 0.002 --tp 105000 --sl 92000
"""

import argparse
import sys

from logging_config import setup_logging
from client import get_client
from validators import validate_order_params
from orders import place_order, attach_tp_sl

logger = setup_logging()


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Place orders on Binance Futures Testnet (USDT-M)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python main.py BTCUSDT BUY MARKET 0.002
  python main.py ETHUSDT SELL LIMIT 0.05 --price 3200
  python main.py BTCUSDT BUY MARKET 0.002 --tp 105000 --sl 92000
  python main.py BTCUSDT BUY STOP_LIMIT 0.002 --price 100000 --stop-price 99500
        """,
    )
    parser.add_argument("symbol", type=str, help="Trading pair (e.g. BTCUSDT)")
    parser.add_argument("side", type=str, help="Order side: BUY or SELL")
    parser.add_argument("type", type=str, help="Order type: MARKET, LIMIT, or STOP_LIMIT")
    parser.add_argument("quantity", type=float, help="Amount of the asset to trade")
    parser.add_argument("--price", type=float, default=None, help="Limit price (required for LIMIT & STOP_LIMIT)")
    parser.add_argument("--stop-price", type=float, default=None, dest="stop_price", help="Stop trigger price (required for STOP_LIMIT)")
    parser.add_argument("--tp", type=float, default=None, help="Take-profit price (auto-closes position at target)")
    parser.add_argument("--sl", type=float, default=None, help="Stop-loss price (auto-closes position at stop)")
    return parser


def print_order_summary(params: dict) -> None:
    """Pretty-print the order request before sending."""
    print("\n" + "=" * 50)
    print("  [ORDER SUMMARY]")
    print("=" * 50)
    print(f"  Symbol      : {params['symbol']}")
    print(f"  Side        : {params['side']}")
    print(f"  Type        : {params['order_type']}")
    print(f"  Quantity    : {params['quantity']}")
    if params.get("price"):
        print(f"  Price       : {params['price']}")
    if params.get("stop_price"):
        print(f"  Stop Price  : {params['stop_price']}")
    if params.get("take_profit"):
        print(f"  Take-Profit : {params['take_profit']}")
    if params.get("stop_loss"):
        print(f"  Stop-Loss   : {params['stop_loss']}")
    print("=" * 50 + "\n")


def print_order_result(response: dict) -> None:
    """Pretty-print the API response after order placement."""
    print("\n" + "=" * 50)
    print("  [ORDER PLACED SUCCESSFULLY]")
    print("=" * 50)
    print(f"  Order ID    : {response.get('orderId', 'N/A')}")
    print(f"  Status      : {response.get('status', 'N/A')}")
    print(f"  Symbol      : {response.get('symbol', 'N/A')}")
    print(f"  Side        : {response.get('side', 'N/A')}")
    print(f"  Type        : {response.get('type', 'N/A')}")
    print(f"  Quantity    : {response.get('origQty', 'N/A')}")
    print(f"  Price       : {response.get('price', 'N/A')}")
    print(f"  Avg Price   : {response.get('avgPrice', 'N/A')}")
    print(f"  Executed Qty: {response.get('executedQty', 'N/A')}")
    print("=" * 50 + "\n")


def print_tp_sl_result(tp_sl: dict) -> None:
    """Pretty-print TP/SL order results."""
    if tp_sl.get("take_profit"):
        tp = tp_sl["take_profit"]
        print("  -- TAKE-PROFIT --")
        print(f"  Order ID    : {tp.get('orderId', 'N/A')}")
        print(f"  Status      : {tp.get('status', 'N/A')}")
        print(f"  Stop Price  : {tp.get('stopPrice', 'N/A')}")
    if tp_sl.get("stop_loss"):
        sl = tp_sl["stop_loss"]
        print("  -- STOP-LOSS --")
        print(f"  Order ID    : {sl.get('orderId', 'N/A')}")
        print(f"  Status      : {sl.get('status', 'N/A')}")
        print(f"  Stop Price  : {sl.get('stopPrice', 'N/A')}")
    print("=" * 50 + "\n")


def main() -> None:
    """Parse CLI args, validate, and execute the order."""
    parser = build_parser()
    args = parser.parse_args()

    # ── Validate ──────────────────────────────────────────────────────────
    try:
        params = validate_order_params(args)
    except ValueError as exc:
        logger.error("Validation failed: %s", exc)
        print(f"\n[ERROR] Validation error: {exc}")
        sys.exit(1)

    # ── Print summary ─────────────────────────────────────────────────────
    print_order_summary(params)
    logger.info("Order validated  →  %s", params)

    # ── Execute primary order ──────────────────────────────────────────
    try:
        client = get_client()
        response = place_order(client, params)
        print_order_result(response)
    except Exception as exc:
        logger.error("Order execution failed: %s", exc)
        print(f"\n[ERROR] Order failed: {exc}")
        sys.exit(1)

    # ── Attach TP/SL if requested ──────────────────────────────────────
    if params.get("take_profit") or params.get("stop_loss"):
        try:
            tp_sl = attach_tp_sl(client, params)
            print_tp_sl_result(tp_sl)
        except Exception as exc:
            logger.error("TP/SL placement failed: %s", exc)
            print(f"\n[WARNING] Primary order placed, but TP/SL failed: {exc}")
            sys.exit(1)


if __name__ == "__main__":
    main()
