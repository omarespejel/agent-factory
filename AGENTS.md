# AGENTS.md

## Project Overview
Autonomous AI agent building a Starknet Monero light client verifier.
Multi-model: GLM-4.7-Flash (coder), Qwen2.5-Coder-32B (reviewer/architect).

## Build Commands
```bash
cd project && scarb build
cd project && snforge test
```

## Code Style
- Cairo `2024_07` edition
- NatSpec on all public functions
- OpenZeppelin v3.0.0 only
- No custom cryptography

## Workflow Rules
1. Query Perplexity before crypto implementation.
2. Call Cairo Coder MCP before any Cairo code change.
3. Call OpenZeppelin MCP for contract patterns or security components.
4. Run `scarb build` and `snforge test` after every Cairo change.
5. Reviewer approval required before commit.

## Manager Protocol
1. Read `.manager/guidance.md` before starting work.
2. Append progress to `.manager/report.md` after significant actions.
3. Run `make manager-tick` after each action.
4. If stuck 3x, run `make manager-force` and wait for guidance.

## Boundaries
- Never implement EC math, hashes, or RNG.
- Never skip build/test gates.
- Mark uncertainty as `NEEDS_HUMAN_REVIEW`.
