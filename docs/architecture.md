# Architecture Deep Dive

## System Overview

This project uses a multi-agent architecture where specialized AI agents collaborate to build a Starknet Monero light client. Each agent has a specific role and uses different models optimized for their task.

## Agent Roles

### 1. Architect Agent (Qwen2.5-Coder-32B)
**Purpose:** High-level design and planning

**Responsibilities:**
- Break down requirements into implementable modules
- Design Cairo contract structure
- Define interfaces and data structures
- Enforce security patterns from the start

**Why Qwen2.5:** Known for being honest about limitations and not hallucinating. Critical for architectural decisions.

### 2. Coder Agent (GLM-4.7-Flash)
**Purpose:** Implementation

**Responsibilities:**
- Write Cairo code based on Architect specs
- Implement modules with proper documentation
- Write tests alongside implementation

**Why GLM-4.7-Flash:** 
- Fastest inference (220 tok/s vs 30-50 for Qwen)
- Best tool calling abilities
- 128K context window

**Known Limitation:** May try to recreate library functionality instead of using imports. This is mitigated by Reviewer.

### 3. Reviewer Agent (Qwen2.5-Coder-32B)
**Purpose:** Quality control and library enforcement

**Responsibilities:**
- Review all code before commit
- Ensure OpenZeppelin imports are used
- Catch cases where Coder reinvented functionality
- Verify documentation completeness

**Why Qwen2.5:** Explicitly good at acknowledging limitations instead of hallucinating solutions.

### 4. Auditor #1: Perplexity MCP
**Purpose:** Security reasoning and best practices

**Responsibilities:**
- Verify patterns against known vulnerabilities
- Research best practices before implementation
- Check for security advisories on dependencies

**Why Perplexity:** Provides reasoned answers with citations, not just search results.

### 5. Auditor #2: Cairo Static Analysis
**Purpose:** Automated vulnerability scanning

**Responsibilities:**
- Run static analysis on all code
- Check for common Cairo vulnerabilities
- Verify formatting and style

**Tools:** `scarb fmt --check`, `snforge test`, Cairo analyzer

## Mandatory Tooling Gates

- **Cairo Coder MCP** must be called before any Cairo code is created or changed.
- **OpenZeppelin MCP** must be called for contract patterns, access control, and security components.
- After every Cairo edit: run `scarb build` and `snforge test`. No exceptions.
- If a gate fails, the agent must stop and fix before continuing.

## Dual-Model Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    WHY TWO MODELS?                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  GLM-4.7-Flash                 Qwen2.5-Coder-32B           │
│  ─────────────                 ──────────────────           │
│  ✅ Fast (220 tok/s)           ✅ Accurate                  │
│  ✅ Great tool calling         ✅ Honest about limits       │
│  ✅ 128K context               ✅ Library-aware             │
│  ⚠️ May skip libraries         ⚠️ Slower (30 tok/s)        │
│                                                             │
│  USED FOR:                     USED FOR:                    │
│  -  Writing code                -  Architecture               │
│  -  Fast iteration              -  Code review                │
│  -  Tool execution              -  Library enforcement        │
│                                                             │
│           GLM writes fast → Qwen reviews carefully          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Dual-Auditor Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    WHY TWO AUDITORS?                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Perplexity MCP                Cairo Static Analysis        │
│  ──────────────                ─────────────────────        │
│  TYPE: Reasoning               TYPE: Scanning               │
│                                                             │
│  CATCHES:                      CATCHES:                     │
│  -  Logic flaws                 -  Known CVEs                 │
│  -  Bad patterns                -  Hardcoded secrets          │
│  -  Missing validations         -  Style violations           │
│  -  Crypto anti-patterns        -  Common bugs                │
│                                                             │
│  ASKS:                         RUNS:                        │
│  "Is this pattern secure?"     scarb fmt --check            │
│  "Known vulns in X?"           scarb test                   │
│                                                             │
│        Reasoning + Scanning = Comprehensive Coverage        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
                              ┌──────────────┐
                              │    TASK      │
                              │   (Human)    │
                              └──────┬───────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────┐
│                         ARCHITECT                               │
│                     (Qwen2.5-Coder-32B)                        │
│                                                                 │
│  1. Understand requirements                                     │
│  2. Query Perplexity for best patterns                         │
│  3. Design module structure                                     │
│  4. Define interfaces                                           │
└────────────────────────────────┬───────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────┐
│                          CODER                                  │
│                      (GLM-4.7-Flash)                           │
│                                                                 │
│  1. Receive spec from Architect                                │
│  2. Query Perplexity before crypto code                        │
│  3. Write implementation with OZ imports                       │
│  4. Write tests (TDD)                                          │
└────────────────────────────────┬───────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│       AUDITOR #1         │  │       AUDITOR #2         │
│    (Perplexity MCP)      │  │   (Cairo Static)         │
│                          │  │                          │
│  -  Security reasoning    │  │  -  scarb fmt --check     │
│  -  Pattern verification  │  │  -  scarb test            │
│  -  Vuln research         │  │  -  Automated scans       │
└────────────┬─────────────┘  └────────────┬─────────────┘
             │                              │
             └──────────────┬───────────────┘
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                         REVIEWER                                │
│                     (Qwen2.5-Coder-32B)                        │
│                                                                 │
│  CHECKLIST:                                                     │
│  □ All functions have NatSpec docs                             │
│  □ Tests exist and pass                                        │
│  □ OpenZeppelin imports used (not reimplemented)               │
│  □ No custom crypto                                            │
│  □ Both auditors approved                                      │
└────────────────────────────────┬───────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
             ┌─────────────┐           ┌─────────────┐
             │   FAILED    │           │   PASSED    │
             │  (Loop back │           │  (Commit)   │
             │  to Coder)  │           └──────┬──────┘
             └─────────────┘                  │
                                              ▼
                                       ┌─────────────┐
                                       │   GITHUB    │
                                       │   COMMIT    │
                                       └──────┬──────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │  NEXT TASK  │
                                       └─────────────┘
```

## Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY ONION                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 5: HUMAN APPROVAL (Telegram)                        │
│           └─ Critical crypto decisions                      │
│                                                             │
│  Layer 4: REVIEWER (Qwen2.5)                               │
│           └─ Library enforcement, code quality              │
│                                                             │
│  Layer 3: AUDITOR #2 (Static Analysis)                     │
│           └─ Automated vulnerability scanning               │
│                                                             │
│  Layer 2: AUDITOR #1 (Perplexity)                          │
│           └─ Security reasoning, pattern verification       │
│                                                             │
│  Layer 1: CODER CONSTRAINTS (System Prompt)                │
│           └─ Must use OZ, must query before crypto          │
│                                                             │
│  Layer 0: LIBRARY CHOICE (OpenZeppelin v3.0.0)             │
│           └─ Audited foundation                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Monero Light Client Components

### Component 1: Ring Signature Verifier
Verifies that a transaction was signed by one of N possible signers without revealing which one.

```
Input: Ring signature, message, public keys
Output: Boolean (valid/invalid)

Security: Must use audited EC operations
```

### Component 2: Pedersen Commitments
Verifies that committed amounts are valid without revealing the amounts.

```
Input: Commitment, blinding factor proof
Output: Boolean (valid/invalid)

Security: Use Cairo's native pedersen hash
```

### Component 3: Key Image Tracker
Prevents double-spending by tracking unique key images.

```
Input: Key image
Output: Boolean (seen/not seen)

Storage: Mapping of key images
Security: Must be append-only, no deletions
```

### Component 4: Transaction Validator
Combines all components to validate a full Monero transaction proof.

```
Input: Transaction proof bundle
Output: Boolean (valid/invalid)

Calls: Verifier, Commitments, KeyImages
```

## File Structure

```
starknet-monero-agent/
├── README.md                 # Project overview
├── config.toml              # OpenHands configuration
├── system_prompt.md         # Agent instructions
├── launch.py                # Agent launcher
├── .env.template            # Environment template
│
├── scripts/
│   ├── setup-runpod.sh     # Full environment setup
│   └── launch.sh           # Start agents in tmux
│
├── docs/
│   ├── architecture.md     # This file
│   └── security.md         # Security decisions log
│
├── logs/
│   ├── ollama.log          # Model server logs
│   └── agent.log           # Agent activity logs
│
└── project/                 # Cairo project (agent-written)
    ├── Scarb.toml          # Cairo package config
    ├── src/
    │   ├── lib.cairo       # Module exports
    │   ├── attestation/    # Quorum attestation modules
    │   │   ├── event.cairo
    │   │   ├── quorum_verifier.cairo
    │   │   └── relayer_registry.cairo
    │   ├── key_images.cairo # Double-spend prevention
    │   ├── validator.cairo # Integration layer
    │   └── utils.cairo      # Helper functions
    └── tests/
        ├── test_key_images.cairo
        └── test_validator.cairo
```
