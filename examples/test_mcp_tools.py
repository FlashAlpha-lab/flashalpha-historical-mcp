"""Smoke-test the FlashAlpha Historical MCP tools via HTTP.

Walks every documented historical tool with a known-good `at` timestamp
(SPY, 2024-08-05 15:30 ET — the Aug-2024 unwind, plenty of activity in the
chain) and reports PASS / FAIL.

Usage:
    python test_mcp_tools.py YOUR_API_KEY
    FLASHALPHA_API_KEY=key python test_mcp_tools.py
"""

from __future__ import annotations

import os
import sys
from typing import Any

try:
    import requests
except ImportError:
    print("Error: 'requests' is not installed. Run: pip install requests")
    sys.exit(1)

MCP_URL = "https://historical.flashalpha.com/mcp"

TEST_TICKER = os.environ.get("TEST_TICKER", "SPY")
TEST_AT = os.environ.get("TEST_AT", "2024-08-05T15:30:00")
TEST_DATE = os.environ.get("TEST_DATE", "2024-08-05")  # for daily tools

PASS = "PASS"
FAIL = "FAIL"


def get_api_key() -> str:
    if len(sys.argv) > 1:
        return sys.argv[1]
    key = os.environ.get("FLASHALPHA_API_KEY", "")
    if not key:
        print(
            "Error: No API key provided.\n"
            "Usage: python test_mcp_tools.py YOUR_API_KEY"
        )
        sys.exit(1)
    return key


def call_tool(session: requests.Session, tool: str, args: dict[str, Any]) -> dict:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": args},
    }
    resp = session.post(MCP_URL, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def run(session: requests.Session, tool: str, args: dict[str, Any]) -> str:
    try:
        result = call_tool(session, tool, args)
        if "error" in result:
            return f"{FAIL}  {tool}  → {result['error']}"
        return f"{PASS}  {tool}"
    except Exception as exc:
        return f"{FAIL}  {tool}  → {exc}"


def main() -> None:
    api_key = get_api_key()
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})

    base = {"apiKey": api_key, "symbol": TEST_TICKER, "at": TEST_AT}
    quote = {"apiKey": api_key, "ticker": TEST_TICKER, "at": TEST_AT}

    cases: list[tuple[str, dict[str, Any]]] = [
        ("historical_tickers",          {"apiKey": api_key}),
        ("historical_tickers",          {"apiKey": api_key, "symbol": TEST_TICKER}),
        ("historical_stock_quote",      quote),
        ("historical_option_quote",     {**quote, "expiry": TEST_DATE, "strike": 540, "type": "C"}),
        ("historical_surface",          base),
        ("historical_gex",              base),
        ("historical_dex",              base),
        ("historical_vex",              base),
        ("historical_chex",             base),
        ("historical_exposure_summary", base),
        ("historical_exposure_levels",  base),
        ("historical_narrative",        base),
        ("historical_zero_dte",         base),
        ("historical_max_pain",         base),
        ("historical_stock_summary",    base),
        ("historical_volatility",       base),
        ("historical_adv_volatility",   base),
        ("historical_vrp",              base),
    ]

    print(f"Testing {len(cases)} tools at {MCP_URL}")
    print(f"  ticker:    {TEST_TICKER}")
    print(f"  as-of:     {TEST_AT}")
    print()
    for tool, args in cases:
        print(run(session, tool, args))


if __name__ == "__main__":
    main()
