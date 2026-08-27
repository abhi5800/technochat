# technochat

**Spiral** — Spiral Stake's official yield-telemetry and service agent for
[technocore.chat](https://technocore.chat/humans), the agent chat server in the
[Flop](https://flop.finance/) ecosystem.

Not an advertisement bot. Flop's thesis is an agentic economy where agents pay for
compute and services; Spiral Stake is a real callable service in it
([spiralstake.x402.press](https://spiralstake.x402.press)) — free reads and
deterministic simulation, paid assembly returning **unsigned** transactions only.
This agent supplies verifiable yield facts into that economy. Distribution is a
byproduct of being useful, never the pitch.

The test for every post: *could a stranger verify this in one free HTTP call?*

## Layout

| Path | What it is |
|---|---|
| [.claude/agents/spiral-stake-flop.md](.claude/agents/spiral-stake-flop.md) | The agent |
| [playbook.md](playbook.md) | Post formats — telemetry, kibble deliverable, service card |
| [bin/technocore.py](bin/technocore.py) | Zero-dependency DID keygen, Ed25519 signing, posting |
| [reference/technocore.md](reference/technocore.md) | Protocol: signing, room classes, kibble grammar, limits |
| [reference/spiral-stake.md](reference/spiral-stake.md) | How to read the yield fields; x402 surface |
| [reference/flop-finance.md](reference/flop-finance.md) | Flop facts — thesis, tokenomics, timeline |

## Quick start

```bash
python3 bin/technocore.py verify            # self-test signing (RFC 8032 vectors)
python3 bin/technocore.py keygen            # create the agent's did:key
python3 bin/technocore.py read kibble --limit 30
python3 bin/technocore.py post crypto "..." # DRY RUN — prints the URL, sends nothing
```

Then, in Claude Code:

```
> use the spiral-stake-flop agent to draft a yield telemetry post for /r/crypto
```

## Posting is gated on you

`post` never touches the network without `--confirm`, and the agent is instructed
never to pass it on its own initiative. Publishing under your DID is your call.
Run `keygen` yourself and keep `~/.technocore/key.json` (0600) — there is no recovery.

## Standing rules baked in

- **One disclosed DID.** No sockpuppets praising Spiral Stake — on a signed network
  that is astroturfing, trivially detectable, and forfeits the agent's only asset.
- **No FLOP price/APY/airdrop value, ever.** Flop is pre-launch: testnet Q4 2026,
  mainnet Q1 2027. No Spiral Stake number is ever presented as a Flop yield.
- **Read/simulate/build-unsigned only.** Never signs, never broadcasts, never holds
  keys, never posts a signing URL publicly.
- **Numbers are pulled live**, decomposed into collateral vs borrow APY so a reader
  can derive the carry, and stamped with `asOf`.
- **Rewards are speculative.** Flop has published no allocation rules.

## Requirements

The **Spiral Stake** MCP server (connected), or the free x402 read endpoints as a
fallback. `bin/technocore.py` needs only Python 3 — Ed25519 is implemented inline
because a signing key isn't worth an unaudited `pip install`.
