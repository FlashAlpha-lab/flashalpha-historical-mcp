# FlashAlpha Historical MCP Server — Point-in-Time Options Analytics for AI Assistants

Connect Claude, Cursor, Windsurf, or any MCP-compatible AI assistant to the
**FlashAlpha Historical API** — point-in-time replay of every live analytics
endpoint. Ask in natural language what GEX, gamma flip, VRP, narrative, max
pain, or the full stock summary looked like at **any minute back to
2018-04-16**.

> Companion to [`flashalpha-mcp`](https://github.com/FlashAlpha-lab/flashalpha-mcp)
> (live data). Same API key, same response shapes — every tool here just adds
> a required `at` parameter.

---

## What Is This

This repository provides documentation, setup, and test scripts for the
FlashAlpha **Historical** MCP server. The server itself runs at
`https://historical.flashalpha.com/mcp` and is not open source. It exposes
historical replay tools through the Model Context Protocol so AI assistants
can answer point-in-time questions like:

> *"What did SPY dealer positioning look like at the COVID-crash close on
> March 16, 2020?"*

> *"How did the gamma flip move during the Aug 5, 2024 unwind?"*

> *"What was the VRP percentile and harvest score on Jan 9, 2025 at 14:30?"*

> *"Replay every Friday close in Q1 2024 and tell me on which days dealers
> were short gamma."*

Backed by 6.7 B option rows + 2 M+ stock minute-bars + EOD OI / SVI / macro.

---

## Server URL

```
https://historical.flashalpha.com/mcp
```

- **Transport:** Streamable HTTP
- **Protocol version:** MCP 2025-03-26
- **Auth:** API key passed as a parameter on each tool call

---

## Quick Setup

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "flashalpha-historical": {
      "type": "http",
      "url": "https://historical.flashalpha.com/mcp"
    }
  }
}
```

### Claude Code CLI

```bash
claude mcp add flashalpha-historical --transport http https://historical.flashalpha.com/mcp
```

### Cursor

Open **Settings > MCP** and add:

```json
{
  "flashalpha-historical": {
    "transport": "http",
    "url": "https://historical.flashalpha.com/mcp"
  }
}
```

See `examples/cursor_settings.json`.

### VS Code

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "flashalpha-historical": {
      "type": "http",
      "url": "https://historical.flashalpha.com/mcp"
    }
  }
}
```

### Windsurf

Open **Cascade > MCP Servers** and add:

```json
{
  "flashalpha-historical": {
    "transport": "http",
    "url": "https://historical.flashalpha.com/mcp"
  }
}
```

---

## Authentication

Every tool call requires an `apiKey` parameter — same key as live FlashAlpha.
Historical validates against the same user table; **Alpha plan or higher**
on every endpoint. Calls count against your daily plan quota (shared with
the live API).

```
apiKey: "fa_your_key_here"
```

Get a free key at [flashalpha.com](https://flashalpha.com).

---

## Available Tools

Every analytics tool takes a required `at` parameter:

- `at: "2026-03-05T15:30:00"` — minute-level (ET wall-clock)
- `at: "2026-03-05"` — defaults to 16:00 ET (session close)

| Tool | Description |
|---|---|
| `historical_tickers` | Coverage table — every covered symbol with date range, healthy days, gaps |
| `historical_stock_quote` | Stock bid/ask/mid/last at the minute |
| `historical_option_quote` | Option quote(s) + greeks + OI at the minute (filter by `expiry`/`strike`/`type`) |
| `historical_surface` | 50×50 IV surface grid (tenor × log-moneyness) |
| `historical_gex` | Gamma exposure by strike |
| `historical_dex` | Delta exposure by strike |
| `historical_vex` | Vanna exposure by strike |
| `historical_chex` | Charm exposure by strike |
| `historical_exposure_summary` | Net GEX/DEX/VEX/CHEX, gamma flip, regime, ±1% hedging, 0DTE contribution |
| `historical_exposure_levels` | Gamma flip, call/put walls, max +/- gamma, highest-OI strike |
| `historical_narrative` | Verbal analysis + prior-day GEX comparison + VIX context |
| `historical_zero_dte` | 0DTE expected move, pin risk, hedging, decay, flow |
| `historical_max_pain` | Pain curve, OI breakdown, dealer alignment, pin probability |
| `historical_stock_summary` | Composite — price, vol, flow, exposure, macro |
| `historical_volatility` | Realized-vs-implied ladder, skew profiles, term structure |
| `historical_adv_volatility` | SVI parameters, variance surface, arbitrage flags, variance swap fairs |
| `historical_vrp` | VRP dashboard with leak-free percentiles (date-bounded) |

See [`docs/api.md`](docs/api.md) for full parameter & response shapes.

---

## Example Prompts

```
> What was SPY's gamma flip relative to spot at 15:30 ET on March 16, 2020?

> Compare SPY's exposure regime at the close of every trading day in
  March 2020. Flag transitions between positive_gamma and negative_gamma.

> Pull the VRP dashboard for SPY on 2024-08-05 at 14:00 ET. What was the
  z-score, harvest score, and dealer flow risk?

> Show me SPY's max pain strike at every Friday close in 2024 and how
  often spot landed within 1% of it.

> What did the 0DTE chain look like 30 minutes before the FOMC announcement
  on 2024-09-18?
```

---

## Coverage

- **Symbols:** SPY (more on demand)
- **Range:** 2018-04-16 → 2026-04-02 (extended forward as new data is published)
- **Granularity:** 1-minute option quotes, greeks, stock bars; EOD OI / SVI /
  macro

---

## Known Gaps from Live (intentional, documented)

- `option_quote.bidSize` / `askSize` / `volume` — always `0`
- `option_quote.svi_vol` — `null` (`svi_vol_gated: "backtest_mode"`)
- `gex.call_volume` / `put_volume` — always `0`; OI changes always `null`
- `narrative.data.top_oi_changes` — empty array
- `stock_summary.macro.vix_futures` / `fear_and_greed` — `null`
- `vrp.macro.hy_spread` — hard-coded `3.5`
- 0DTE intraday greeks (delta/gamma/theta/iv) often `0` / `null`

---

## License

MIT
