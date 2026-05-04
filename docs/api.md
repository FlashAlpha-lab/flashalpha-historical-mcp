# FlashAlpha Historical MCP — Tool Reference

This document mirrors the underlying REST API at
[`https://historical.flashalpha.com`](https://historical.flashalpha.com).

Every analytics tool below takes:

- `apiKey` (string, required) — same FlashAlpha API key used for live
- `at` (string, required) — as-of timestamp:
    - `"yyyy-MM-ddTHH:mm:ss"` — minute-level (ET wall-clock)
    - `"yyyy-MM-dd"` — defaults to 16:00 ET (session close)

---

## Coverage

### `historical_tickers`

Lists every covered symbol with its date range, healthy day count, and gap
breakdown.

| Param | Type | Required | Description |
|---|---|---|---|
| `apiKey` | string | yes | |
| `symbol` | string | no | Filter to a single symbol |

---

## Market Data

### `historical_stock_quote`

Stock bid/ask/mid/last at the requested minute.

### `historical_option_quote`

Option quote(s) + greeks + OI at the minute.

| Param | Type | Required | Description |
|---|---|---|---|
| `apiKey` | string | yes | |
| `ticker` | string | yes | |
| `at` | string | yes | |
| `expiry` | string | no | `yyyy-MM-dd` |
| `strike` | number | no | |
| `type` | string | no | `C` / `Call` / `P` / `Put` |

**Known gaps:** `bidSize` / `askSize` / `volume` always `0`. `svi_vol`
always `null` (`svi_vol_gated: "backtest_mode"`).

### `historical_surface`

50×50 implied-vol surface grid (tenor × log-moneyness). Returns 404
`insufficient_data` for sparse historical days (pre-2018 low-volume symbols).

---

## Exposure Analytics

### `historical_gex` / `historical_dex` / `historical_vex` / `historical_chex`

Greek exposure by strike (gamma / delta / vanna / charm).

| Param | Required | Description |
|---|---|---|
| `apiKey` | yes | |
| `symbol` | yes | |
| `at` | yes | |
| `expiration` | no | Filter to single expiry |
| `min_oi` | no (gex only) | OI threshold |

**Known gaps:** `call_volume` / `put_volume` always `0`; `call_oi_change` /
`put_oi_change` always `null`.

### `historical_exposure_summary`

Net GEX/DEX/VEX/CHEX, gamma flip, regime, ±1% hedging, 0DTE contribution,
verbal interpretations.

### `historical_exposure_levels`

Gamma flip, max +/- gamma, call/put walls, highest-OI strike, 0DTE magnet.

### `historical_narrative`

Verbal analysis + prior-day GEX comparison + VIX context. `gex_change` pulls
the previous trading day's net GEX; `vix` is the closing value for the
trading day of `at`.

**Known gap:** `narrative.data.top_oi_changes` is always an empty array.

### `historical_zero_dte`

0DTE-specific analytics — regime, expected move, pin risk, hedging, decay,
flow, levels, strikes. `time_to_close_hours` is computed from `at` against
16:00 ET on the same day, so theta and greek-acceleration values are
minute-accurate.

| Param | Required | |
|---|---|---|
| `apiKey` / `symbol` / `at` | yes | |
| `strike_range` | no | Strike-pct band around spot |

**Known gap:** intraday 0DTE greeks (delta/gamma/theta/iv) often `0` / `null`
for very-near-expiry contracts at minute resolution.

---

## Max Pain

### `historical_max_pain`

Strike-by-strike pain curve, OI breakdown, dealer alignment, expected move
context, pin probability, multi-expiry calendar.

---

## Composite

### `historical_stock_summary`

The big one — price, vol (ATM IV, HV20, HV60, VRP, 25d skew, IV term),
options flow, full exposure block, macro context.

**Known gaps:** `total_call_volume` / `total_put_volume` / `pc_ratio_volume`
all `0` / `null`. `macro.vix_futures` / `fear_and_greed` always `null`.

---

## Volatility

### `historical_volatility`

Realized vol ladder (5/10/20/30/60d), IV-RV spreads, skew profiles per
expiry, term structure, IV dispersion, GEX/theta by DTE bucket.

### `historical_adv_volatility`

SVI parameters, forward prices, total variance surface, arbitrage flags,
variance swap fair values, greek surfaces (vanna/charm/volga/speed).

---

## VRP

### `historical_vrp`

VRP dashboard with **date-bounded** percentile history — only snapshots
dated strictly before `at` are included, so percentile and z-score reflect
what was knowable at that moment (no future leakage).

**Known gap:** `macro.hy_spread` is currently a fixed `3.5` on historical
responses (the high-yield spread isn't yet served by the historical macro
feed).

---

## Errors

| Status | Code | When |
|---|---|---|
| 400 | `invalid_at` | Missing or malformed `at` |
| 401 | — | Bad `apiKey` |
| 403 | `tier_restricted` | User tier below Alpha |
| 404 | `symbol_not_found` | Symbol has no data at `at` |
| 404 | `no_coverage` | Symbol not in historical dataset |
| 404 | `no_data` | `(symbol, at)` outside coverage / inside gap |
| 404 | `insufficient_data` | Surface grid too sparse |
| 429 | — | Daily quota exhausted (shared with live) |

---

## Notes

- **Timezone:** stored `at` values are ET wall-clock. Don't shift by UTC offset.
- **Quota:** Historical calls share your daily plan quota with the live API.
- **Latency:** simple lookups ~50-300 ms; full `adv_volatility` /
  `stock_summary` ~500-1500 ms on cold hits.
