# PLAN.md - Current Development State

## Architecture Decision
**Approach A: Quorum Attestation** (per `docs/spec/monero-verification.md`)

## Manager Protocol
- Manager: GPT-5.2-Codex
- Research: Perplexity sonar-reasoning-pro
- Trigger: Every 3 agent calls OR when stuck

## Current Phase
**Phase 1: Attestation Foundation**

## Phases

### Phase 1: MoneroEventV1 + Quorum Verifier ⬅️ CURRENT
- [x] Define `MoneroEventV1` struct
- [x] Create module structure
- [ ] Implement `compute_event_hash` with domain separation
- [ ] Implement threshold signature verification
- [ ] Tests for hash computation
- [ ] Tests for signature verification

### Phase 2: Relayer Registry
- [ ] Implement `add_relayer` / `remove_relayer`
- [ ] Use OZ Ownable for governance
- [ ] Tests for relayer management

### Phase 3: Key Image Tracker
- [ ] Implement append-only storage
- [ ] Integration with attestation flow
- [ ] Tests for double-spend prevention

### Phase 4: Event Validator (Integration)
- [ ] Combine quorum + key images
- [ ] Full event acceptance flow
- [ ] Integration tests

### Phase 5: Upgradeable Interface
- [ ] Design for future ZK verifier
- [ ] State compatibility

## Completed
- [x] Repo structure
- [x] OZ v3.0.0 integration
- [x] Build/test pipeline
- [x] Spec document
- [x] ADRs (001, 002, 003)
- [x] Manager protocol setup

## Stuck Log
| Date | Module | Issue | Resolution |
|------|--------|-------|------------|
| - | - | - | - |

## Manager Sync History
See `.manager/history/` for archived guidance sessions.
