# Flop Finance — grounding facts

Source: https://flop.finance/ and https://flop.finance/teaser/ (fetched 2026-08-27).
This file exists so the agent quotes facts instead of inventing them. If a claim is
not in this file, the agent says "I don't know" or re-fetches the source.

## What it is

Flop Network is a **proof-of-useful-inference (PoUI)** L1 built by Flop Labs
(founded by Arthur Hayes, BitMEX co-founder) for the **agentic economy** — the
machine-to-machine market where AI agents transact with each other.

$FLOP is positioned as **"food for your AI agent"**: a compute-backed currency,
redeemable on demand for GPU inference. The pitch contrasts it with fiat-backed
stablecoins — FLOP is backed by the one commodity an agent cannot exist without.

Launch model: **no pre-sale, no VCs, 100% fair launch.**

## Status — READ THIS BEFORE QUOTING ANYTHING

| Milestone | Date |
|---|---|
| Testnet | Q4 2026 (~90 days out as of the teaser) |
| Mainnet / genesis block | Q1 2027 |

**There is no live $FLOP token, no FLOP price, no FLOP APY, and no FLOP market
on Morpho or Spiral Stake.** As of 2026-08-27, Spiral Stake lists 33 eligible
strategies on Ethereum mainnet and **none** involve FLOP.

## Tokenomics

- Total supply at Year 10: **17.2B FLOP**
- Genesis airdrop: **3.5B (20.4%)** — miners 1.2B, agents 1.2B, validators 305.5M, reserve 794.5M
- Year-10 allocation: miners 8.8B (51.2%), validators 1.2B (6.8%), brokers/agents 1.2B (6.8%), team+foundation 2.0B (11.4%), staking rewards 0.6B (3.4%)
- Block reward **96 FLOP/block**, ~**1s** block time
- Halving every **730 days** for the first five halvings; constant from Year 6
- Flop Labs LLC and Flop Foundation each take 8 FLOP/block; both **sunset after Year 10**

## Native yield mechanics (protocol-level, not DeFi)

- **Miners** — GPUs with 16GB+ VRAM. Earn block rewards pro-rata to compute plus
  **85% of inference fees** (liquid, no lockup). Must stake FLOP proportional to
  compute capacity. Slashable.
- **Validators** — capped at **1,000**. 8+ core CPU, 64GB RAM, 2TB NVMe, 1Gbps
  redundant. Earn block rewards plus **15% of inference fees**. Must stake.
  Top 50 monthly performers replace the bottom 50 from the waiting queue.
- **Agents** — buy sessions specifying model hash, max latency, FLOPs, a
  confidentiality flag, and a FLOP fee. Subsidised compute during bootstrap.
  Airdrop claim is based on testnet inference spend.
- **Brokers** — demand-side infra, quote fixed-dollar pricing settled in FLOP.
- **Stakers** — plain FLOP holders earn pro-rata from block rewards, **no
  delegation required**. 0.6B FLOP (3.4%) allocated through Year 10.

**No APY figures are published.** Do not compute or imply one.

## Verification stack (four layers)

1. **Hardware attestation (TEE)** — enterprise GPUs cryptographically prove execution
2. **Work certificate (TOPLOC)** — miners commit fingerprints of model activations; validators sample-check
3. **Re-execution** — validators randomly re-run sessions; disputes force full re-execution
4. **Slashing** — miner stake at risk, up to total loss plus permanent ban

## Other primitives

- Native **HTLC** for atomic swaps of FLOP against external chains, enabling
  "agentic sub-economies"
- Governance by **Flop Improvement Protocol (FIP)**, ⅔ validator approval;
  initially only the Flop Foundation may submit

## Market-context numbers the teaser cites

1,000× projected machine-vs-human traffic in 5 years (Cloudflare) · 1,700% YoY
growth in daily agentic AI requests · ~70% of US equity volume is algorithmic ·
150+ A2A protocol member organisations.
