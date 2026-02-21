# Binance Futures Testnet -- Trading Bot

A clean, modular Python CLI application to place **Market**, **Limit**, and **Stop-Limit** orders on **Binance Futures Testnet (USDT-M)**, with built-in **Take-Profit & Stop-Loss** risk management.

---

## Prerequisites

- **Python 3.10+**
- A [Binance Futures Testnet](https://testnet.binancefuture.com) account with API credentials

---

## Quick Start (< 5 min)

```bash
# 1. Clone the repo
git clone <repo-url> && cd BINANCE_AUTOTRADE

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API keys
#    Copy the example and fill in your Testnet credentials:
copy .env.example .env
#    Then edit .env with your keys
```

---

## Usage

```
python main.py <SYMBOL> <SIDE> <TYPE> <QUANTITY> [--price PRICE] [--stop-price STOP_PRICE] [--tp TP] [--sl SL]
```

### Market Order

```bash
python main.py BTCUSDT BUY MARKET 0.001
```

### Limit Order

```bash
python main.py ETHUSDT SELL LIMIT 0.05 --price 3200
```

### Stop-Limit Order (Bonus)

```bash
python main.py BTCUSDT BUY STOP_LIMIT 0.002 --price 100000 --stop-price 99500
```

### Market Order with Take-Profit & Stop-Loss

```bash
python main.py BTCUSDT BUY MARKET 0.002 --tp 70000 --sl 55000
```

This places **3 orders in one command**:
1. A MARKET BUY for 0.002 BTC
2. A TAKE_PROFIT_MARKET SELL at 70,000 (auto-close at target)
3. A STOP_MARKET SELL at 55,000 (auto-close at stop)

`--tp` and `--sl` work with any order type (MARKET, LIMIT, or STOP_LIMIT).

---

## Project Structure

```
BINANCE_AUTOTRADE/
|-- main.py              # CLI entry-point (argparse)
|-- client.py            # Binance Testnet client factory
|-- orders.py            # Order execution + TP/SL attachment
|-- validators.py        # Input validation
|-- config.py            # API keys & constants (loaded from .env)
|-- logging_config.py    # Dual-handler logging (file + console)
|-- requirements.txt     # Pinned dependencies
|-- .env.example         # Template for API credentials
|-- .gitignore
|-- evidence/            # Log evidence of successful test orders
|   |-- market_order.log
|   |-- limit_order.log
|   +-- market_with_tp_sl.log
+-- README.md
```

---

## Logging

All activity is written to **`trading_bot.log`** in the project root. Each entry includes:

| Field | Example |
|---|---|
| Timestamp | `2026-02-21 16:50:00` |
| Level | `INFO` |
| Request payload | `{"symbol": "BTCUSDT", "side": "BUY", ...}` |
| API response | Full JSON from Binance |
| Errors | Stack trace on failure |

---

## Assumptions

- Designed **exclusively** for the Binance Futures **Testnet** -- do not use with live credentials.
- The `python-binance` library handles HMAC signing, timestamps, and request formatting.
- Stop-Limit orders map to Binance's `STOP` order type with `stopPrice` and `price` fields.
- TP/SL orders use `TAKE_PROFIT_MARKET` and `STOP_MARKET` types for guaranteed fills.
- Testnet enforces a minimum notional of ~$100 -- use quantity >= 0.002 for BTCUSDT.

---

## Author

**Rishabh**
* [GitHub Profile](https://github.com/rixabhh)
* [LinkedIn](https://www.linkedin.com/in/rishabbh/)

