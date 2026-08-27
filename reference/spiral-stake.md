# Spiral Stake — how to read the numbers

Spiral Stake exposes **leveraged-yield ("looping") strategies powered by Morpho**.
Every field the MCP server returns is a raw, unit-labelled fact. The only opinion
is namespaced under `spiralHints`, and it always ships its own thresholds — so it
can be overridden rather than trusted.

## The core identity

```
carry            = collateralApyPct - netBorrowApyPct
leverageApyPct   ≈ collateralApyPct + (leverage - 1) x carry
```

Leverage multiplies the **carry**, not the yield. Two consequences that the agent
must never get wrong:

1. **Negative carry can still show a positive `leverageApyPct`**, because the 1x
   base yield dominates until leverage gets large. Read the `leverageLadder` —
   never infer the number.
2. **Positive carry is not safety.** It is a spread between two floating rates,
   and `borrowApyPct` moves on utilisation. At 10x, a 1pp move in borrow cost is
   a ~9pp move in position APY.

## Fields that decide whether a strategy is survivable

| Field | Why it matters |
|---|---|
| `oracle.type` | `nav` prices collateral off redemption value — it shrugs off a DEX depeg. `market` reads a market price and **can liquidate you on a depeg even when the collateral still redeems 1:1.** Weigh against `ltvPct.liquidation` headroom. |
| `ltvPct.liquidation` vs `ltvPct.max` | The gap is the entire buffer. At 86.00 / 85.75 that is 25bps. |
| `exitLiquidity.slippagePct` | Measured **per USD size**, not a single number. `null` = no route at that size. Negative = price improvement. |
| `maxLeverage` | A **liquidity bound, not a safety bound.** 26.7x being offered is not 26.7x being sensible. |
| `utilizationPct` | High utilisation means borrow APY is twitchy and withdrawal can queue. |
| `yieldSustainabilityPct` | 30/60/90d averages of the collateral APY. A spot APY far above its 90d average is a spike, not a rate. |
| `pointsIncentive` | Points are **not** in `collateralApyPct`. Never convert points to APY. |
| `collateral.maturityDaysLeft` | PT collateral pulls to par at maturity; the APY is a fixed yield-to-maturity, not a running rate. |
| `freshness.*.staleAfterSec` | Borrow rates go stale in 300s. Re-read before quoting. |

## Snapshot from 2026-08-27T10:26Z (chain 1, 33 eligible strategies)

Categories: 22 `stable`, 6 `stable-PT`, 4 `ETH`, 1 `BTC`. All `nav` oracles
except **LBTC/WBTC, which is `market`**.

Illustrative spread at the default leverage the app suggests:

- `PT-apyUSD/apxUSD` — 10.5x, **72.63%** (13.82% collat vs 7.63% borrow)
- `PT-USD3/USDC` — 6.7x, **58.53%**
- `sUSDai/AUSD` — 10.5x, **62.44%** (0.91% borrow is the whole story)
- `sUSDe/USDtb` — 10.5x, **-80.77%** — negative carry, leverage amplifying a loss
- `stUSDS/USDT` — 6.7x, **-15.86%**, while `stUSDS/USDS` at the same 6.7x is **+10.13%**

Those last two are the same collateral. The loan asset chose the sign. That is
the single most useful thing to say to another agent about looping.

These numbers are stale the moment they are written down. **Always re-read
`list_strategies` before quoting, and always cite `asOf`.**

## Execution model

Non-custodial and unsigned, end to end.

- `simulate_leverage` — deterministic preview, **no wallet needed**. Always run first.
- `build_leverage_tx` / `build_manage_tx` — return an **unsigned** payload:
  broadcast `approvals[]` first, then `tx{to,data,value}`. The server never signs,
  never sends, and holds no keys. Rebuild if `meta.expiresAt` has passed.
- `meta.signingUrl` is a convenience for a human in the loop, not the canonical output.

Only eligible strategies are returned — thin, near-maturity, no-swap-route, and
zero-APY markets are filtered out before you see them.

## The x402 service surface

Spiral Stake is also a callable, payable HTTP service — "a non-custodial Morpho
leverage-execution gateway behind x402 micropayments" at
**`https://spiralstake.x402.press`**. This is what makes the agent a *supplier*
to the agentic economy rather than a commentator on it.

Discovery: `/openapi.json` · `/llms.txt` · `/.well-known/x402.json` · `/persona`
(machine-readable SOUL) · `/tools`

**Free — every read:**
`GET /v1/strategies` · `POST /v1/strategies` (filters) · `GET /v1/strategies/{id}` ·
`GET /v1/prices` · `POST /v1/simulate` · `GET /v1/positions/{address}` ·
`GET /health` · `GET /about` · `GET|POST /feedback`

**Paid — assembly only:** `$0.006125/call` on Base (per-chain pricing in the x402
manifest), USDC or EURC across Base, Arbitrum, Polygon, Avalanche.

- `POST /v1/build/leverage-tx` — needs `strategyId`, `payToken`, `amount`,
  `userAddress`; optional `leverage`/`desiredLtv`, `slippage`, `chainId`
- `POST /v1/build/manage-tx` — needs `userAddress`, `id`, `action`
  (`close`, `increase_leverage`, `add_collateral`, `remove_collateral`, `repay`, `borrow`)

Both return **unsigned** approvals + transaction + metadata. Two-round HTTP 402
handshake via a central facilitator; no subscriptions, no API keys.

Design principle worth quoting verbatim when other agents ask:
**"No LLM arithmetic: every computed number comes from a compute operation."**

The whole read surface is free, so pointing another agent at it costs them
nothing and costs you nothing. Only assembling a transaction is paid — and that
is the one step a counterparty would actually want to pay for.
