# ADR-003: Quorum Attestation for Monero Events (Approach A)

## Status
Accepted

## Context
We need to verify Monero events on Starknet. Three approaches exist:
- A) Accountable attestation (relayer quorum) — deployable now
- B) Light-client proofs (FlyClient) — requires Monero consensus changes
- C) ZK proofs of Monero validity — major research effort

## Decision
Implement Approach A: accountable attestation with threshold signatures.

## Rationale
Per the specification in `docs/spec/monero-verification.md`:
- On-chain RingCT + Bulletproof verification is impractical
- RandomX PoW verification is too expensive on-chain
- Quorum attestation is deployable now with acceptable trust assumptions
- Architecture supports future upgrade to ZK proofs

## Components
1. `MoneroEventV1` canonical schema
2. Threshold signature verification in Cairo
3. Relayer governance (add/remove)
4. Upgradeable verifier interface (for future ZK)

## Consequences
- Trusts quorum honesty (mitigated by threshold + slashing)
- Enables deployment without Monero consensus changes
- Preserves upgrade path to trustless verification

## References
- `docs/spec/monero-verification.md`
- FlyClient paper: https://eprint.iacr.org/2019/226
