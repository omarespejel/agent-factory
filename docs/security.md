# Security Decisions Log

This document records security-relevant decisions, rationale, and approval checkpoints.

## Principles

1. **No custom cryptography** — All crypto operations use audited libraries
2. **Defense in depth** — Multiple validation layers (Perplexity + Static + Reviewer)
3. **Fail secure** — On uncertainty, stop and request human review
4. **Audit trail** — All security decisions documented here

---

## Decisions Log

### Decision 001: OpenZeppelin Version Selection
- **Date:** 2026-01-28
- **Decision:** Pin to OpenZeppelin Cairo v3.0.0
- **Rationale:** Latest audited release (Dec 2025), full Cairo 1.x support
- **Risk:** Future vulnerabilities in this version
- **Mitigations:** Monitor OZ security advisories, plan upgrade path
- **Human Approval:** ⏳ Pending

### Decision 002: Dual Auditor Architecture
- **Date:** 2026-01-28
- **Decision:** Use Perplexity MCP (reasoning) + Cairo static analysis (scanning)
- **Rationale:** Reasoning catches logic flaws; scanning catches known CVEs
- **Risk:** Neither catches novel attack vectors
- **Mitigations:** Human review of all crypto-critical code via Telegram
- **Human Approval:** ⏳ Pending

### Decision 003: Dual Model Strategy
- **Date:** 2026-01-28
- **Decision:** GLM-4.7-Flash (coder) + Qwen2.5-Coder-32B (reviewer)
- **Rationale:** GLM is fast but may skip libraries; Qwen catches this
- **Risk:** Both models could agree on wrong approach
- **Mitigations:** Perplexity auditor provides third opinion
- **Human Approval:** ⏳ Pending

### Decision 004: No Custom Cryptographic Implementations
- **Date:** 2026-01-28
- **Decision:** Forbid all custom EC, hash, and RNG implementations
- **Rationale:** Custom crypto is the #1 source of vulnerabilities
- **Risk:** May limit functionality if audited libs don't support needed ops
- **Mitigations:** Use Cairo stdlib (pedersen, poseidon) and OZ components
- **Human Approval:** ⏳ Pending

### Decision 005: Mandatory Build/Test Gates
- **Date:** 2026-01-28
- **Decision:** Every Cairo change must pass `scarb build` and `snforge test`
- **Rationale:** Catch errors immediately, prevent broken code from accumulating
- **Risk:** May slow down iteration
- **Mitigations:** Acceptable tradeoff for security
- **Human Approval:** ⏳ Pending

---

## Security Review Checklist

Before any code is considered complete:

- [ ] All functions have NatSpec documentation
- [ ] All public functions have input validation
- [ ] No custom cryptographic implementations
- [ ] OpenZeppelin components used for access control
- [ ] Tests cover all public functions
- [ ] Perplexity audit completed
- [ ] Static analysis passes (`scarb build`, `snforge test`)
- [ ] Reviewer (Qwen2.5) approved

## Template for New Decisions

```
### Decision XXX: [Title]
- **Date:** YYYY-MM-DD
- **Decision:** [What was decided]
- **Rationale:** [Why]
- **Risk:** [What could go wrong]
- **Mitigations:** [How we address the risk]
- **Human Approval:** [Pending/Approved by X on DATE]
```
