"""Smoke-test the FlashAlpha Historical MCP tools via HTTP.

Walks every documented historical tool with a known-good `at` timestamp
(SPY, 2024-08-05 15:30 ET — the Aug-2024 unwind, plenty of activity in the
chain) and reports PASS / FAIL.

Usage:
    python test_mcp_tools.py YOUR_API_KEY
    FLASHALPHA_API_KEY=key python test_mcp_tools.py
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

try:
    import requests
except ImportError:
    print("Error: 'requests' is not installed. Run: pip install requests")
    sys.exit(1)

MCP_URL = "https://lab.flashalpha.com/mcp"

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
    return rpc(session, payload)


def rpc(session: requests.Session, payload: dict[str, Any]) -> dict:
    resp = session.post(MCP_URL, json=payload, timeout=60)
    resp.raise_for_status()
    if "mcp-session-id" in resp.headers:
        session.headers["mcp-session-id"] = resp.headers["mcp-session-id"]
    if resp.headers.get("content-type", "").startswith("text/event-stream"):
        lines = [line[5:].strip() for line in resp.text.splitlines() if line.startswith("data:")]
        return json.loads(lines[-1])
    return resp.json()


def initialize(session: requests.Session) -> None:
    rpc(session, {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "initialize",
        "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "test_mcp_tools", "version": "1"}},
    })


def payload_problem(result: dict[str, Any]) -> str | None:
    """Upstream failures arrive as ordinary text, so a pass has to mean data came back."""
    body = result.get("result", {})
    parts = [part.get("text", "") for part in body.get("content", []) if part.get("type") == "text"]
    text = "\n".join(parts).strip()
    if body.get("isError") or not text:
        return text[:160] or "empty result"
    try:
        payload = json.loads(text)
    except ValueError:
        return text[:160]
    if isinstance(payload, dict) and (payload.get("status") == "ERROR" or payload.get("error")):
        return str(payload.get("message") or payload.get("error"))[:160]
    return None


def run(session: requests.Session, tool: str, args: dict[str, Any]) -> str:
    try:
        result = call_tool(session, tool, args)
        if "error" in result:
            return f"{FAIL}  {tool}  → {result['error']}"
        problem = payload_problem(result)
        if problem:
            return f"{FAIL}  {tool}  → {problem}"
        return f"{PASS}  {tool}"
    except Exception as exc:
        return f"{FAIL}  {tool}  → {exc}"


def main() -> None:
    api_key = get_api_key()
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    initialize(session)

    base = {"apiKey": api_key, "symbol": TEST_TICKER, "at": TEST_AT}
    quote = {"apiKey": api_key, "symbol": TEST_TICKER, "at": TEST_AT}

    cases: list[tuple[str, dict[str, Any]]] = [
        ("get_historical_coverage",          {"apiKey": api_key}),
        ("get_historical_coverage",          {"apiKey": api_key, "symbol": TEST_TICKER}),
        ("get_historical_stock_quote",      quote),
        ("get_historical_option_quote",     {**quote, "expiry": TEST_DATE, "strike": 540, "type": "C"}),
        ("get_historical_surface",          base),
        ("get_historical_gex",              base),
        ("get_historical_dex",              base),
        ("get_historical_vex",              base),
        ("get_historical_chex",             base),
        ("get_historical_exposure_summary", base),
        ("get_historical_levels",  base),
        ("get_historical_narrative",        base),
        ("get_historical_zero_dte",         base),
        ("get_historical_max_pain",         base),
        ("get_historical_stock_summary",    base),
        ("get_historical_volatility",       base),
        ("get_historical_advanced_volatility",   base),
        ("get_historical_vrp",              base),
    ]

    print(f"Testing {len(cases)} tools at {MCP_URL}")
    print(f"  ticker:    {TEST_TICKER}")
    print(f"  as-of:     {TEST_AT}")
    print()
    results = [run(session, tool, args) for tool, args in cases]
    print("\n".join(results))
    failed = sum(line.startswith(FAIL) for line in results)
    print(f"\n{len(results) - failed} passed, {failed} failed")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
