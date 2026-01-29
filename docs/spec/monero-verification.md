# Monero Verification Specification (Approach A)

This document is the source of truth for the on-chain verification approach.

**Approach A: Quorum Attestation**
- Off-chain relayers verify Monero events via RPC.
- On-chain Cairo verifies a threshold of relayer signatures.

**Rationale (summary):**
- On-chain RingCT/Bulletproof verification is impractical.
- On-chain RandomX PoW verification is too expensive.
- Quorum attestation is deployable now with acceptable trust assumptions.
- Architecture preserves an upgrade path to trustless proofs later.

## 1. MoneroEventV1 schema

`MoneroEventV1` is the canonical event structure signed by relayers and verified
on-chain. All components MUST use this exact field order.

**Fields (in order):**

| Field | Type | Description |
| --- | --- | --- |
| `chain_id` | `felt252` | Monero network identifier (see rules below). |
| `swap_id` | `felt252` | Swap identifier from Starknet state. |
| `txid_high` | `felt252` | High 128 bits of the Monero txid. |
| `txid_low` | `felt252` | Low 128 bits of the Monero txid. |
| `output_index` | `u32` | Output index in the transaction. |
| `amount_atomic` | `u128` | Amount in atomic units. |
| `lock_height` | `u64` | Block height where the tx is included. |
| `confirmations` | `u32` | Confirmations observed at signing time. |
| `timestamp` | `u64` | Block timestamp in seconds. |
| `deadline` | `u64` | Latest acceptable signature time (seconds). |

### Normative rules

- **Field order**: Serialization and hashing MUST follow the field order above.
- **Numeric encoding**: All integers are unsigned. Off-chain components encode
  integers in big-endian when converting bytes to integers.
- **`chain_id`**: Use ASCII bytes of the canonical string (e.g. `monero-mainnet`,
  `monero-stagenet`, `monero-testnet`) interpreted as a big-endian integer.
- **`txid` split**: Decode the 32-byte txid hex string in canonical order
  (most significant byte first). `txid_high` is the first 16 bytes, and
  `txid_low` is the last 16 bytes, both as big-endian integers.
- **Domain separator + hash**: `event_hash` MUST be computed as a domain-
  separated hash over the ordered fields. Use the felt constant
  `MONERO_EVENT_V1` followed by all fields in order, hashed with the same
  function in every component (Cairo Poseidon recommended).
- **Signature scheme**: Use Starknet ECDSA over the Stark curve. Each signature
  is an `(r, s)` pair of `felt252`. Public keys are Starknet-style `felt252`
  x-coordinates.
- **Threshold semantics**: The threshold is the count of **independent** valid
  signatures from **distinct** relayer public keys. No aggregation is assumed.
  Duplicate signers or duplicate signatures MUST NOT be counted.
- **Replay protection**: Contracts MUST reject any event that reuses an already
  accepted `(chain_id, swap_id)` **or** `(chain_id, txid_high, txid_low,
  output_index)` tuple.

## 2. Quorum attestation

Relayers verify a Monero event off-chain, compute `event_hash` from
`MoneroEventV1`, and submit their signatures on-chain. Cairo verifies that a
threshold of authorized relayers signed the same `event_hash`.

## 3. Governance & Ops

Governance controls relayer registration, key rotation, and threshold updates.
Operational policy MUST minimize mismatches across watchtower, Rust, and Cairo.

### Relayer policy

- **Reorg handling**: Relayers MUST only sign once `confirmations >=
  MIN_CONFIRMATIONS` (governance-set). If a reorg invalidates a signed event
  before `deadline`, relayers MUST publish correction evidence within the
  dispute window.
- **Evidence storage**: Persist `event_hash` along with a hash of the
  signature list, relayer set, and RPC evidence (e.g., block header + tx
  proof). Phase 2 should store a single `evidence_hash` per accepted event.
- **Slashing triggers**: Slash relayers that sign (a) invalid hashes for the
  declared fields, (b) events with insufficient confirmations, (c) conflicting
  events for the same `(chain_id, swap_id)` or `(chain_id, txid, output_index)`,
  or (d) events past `deadline`.
