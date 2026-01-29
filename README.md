# 🤖 Starknet Monero Light Client - Autonomous AI Build

> An experiment: Can AI agents autonomously build a production-grade Starknet Monero light client?

![Status](https://img.shields.io/badge/Status-In%20Progress-yellow)
![Models](https://img.shields.io/badge/Models-GLM--4.7--Flash%20%2B%20Qwen2.5-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 The Experiment

**Rules:**
- Zero human-written code in `project/`
- Dual AI models (coder + reviewer)
- Dual auditors (reasoning + scanning)
- OpenZeppelin patterns only
- 6+ hours of autonomous work

**Goal:** Trustless Monero verification on Starknet.

## 📌 Repo Scope

This repository is a **documentation-first logbook** of a remote, autonomous build. It includes setup, architecture, prompts, and a minimal Cairo scaffold. Execution happens on a RunPod GPU, and runtime artifacts are not committed.

**Not stored here:**
- API keys or secrets
- Model weights or large artifacts
- Raw runtime logs

## 🧭 Manager Protocol

The repo includes a lightweight manager loop that periodically summarizes progress and provides guidance.

**Key files:**
- `.manager/` — guidance, reports, history (generated)
- `scripts/manager_sync.py` — manager sync + research
- `prompts/manager.md` — manager prompt

**Core commands:**
```bash
make manager-force     # Force a new manager sync
make manager-check     # Check if sync is needed
make manager-tick      # Increment call count after actions
make research Q="..."  # Perplexity research
```

## 🧩 Local vs RunPod Split

**Local machine (no GPU):**
- Edit code, review, git operations
- Run `make context`, `make manager-force`, `make research Q="..."`
- Read `.manager/guidance.md`
- Run `scarb build` / `snforge test` if toolchain is installed

**RunPod VM (GPU):**
- Run Ollama + OpenHands agents
- Agents read `.manager/guidance.md`, write `.manager/report.md`
- Agents run `make manager-tick` after actions
- Run `scarb build` / `snforge test` as part of agent workflow

**Why split:** Manager/research calls are API-based and do not need GPU time.
Keep those local to avoid idle GPU costs.

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   RUNPOD (L40S 48GB · $0.87/hr)              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              OPENHANDS (Orchestrator)                 │   │
│  └───────────────────────┬──────────────────────────────┘   │
│                          │                                   │
│       ┌──────────────────┼──────────────────┐               │
│       ▼                  ▼                  ▼               │
│  ┌─────────┐       ┌─────────┐       ┌─────────┐           │
│  │ARCHITECT│       │ CODER   │       │REVIEWER │           │
│  │Qwen2.5  │       │GLM-4.7  │       │Qwen2.5  │           │
│  └─────────┘       └─────────┘       └─────────┘           │
│                          │                                   │
│       ┌──────────────────┼──────────────────┐               │
│       ▼                  ▼                  ▼               │
│  ┌─────────┐       ┌─────────┐       ┌─────────┐           │
│  │AUDITOR 1│       │AUDITOR 2│       │ TESTER  │           │
│  │Perplexity│      │ Static  │       │         │           │
│  └─────────┘       └─────────┘       └─────────┘           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| **Primary Coder** | GLM-4.7-Flash | Fast (220 tok/s), best tool calling |
| **Reviewer** | Qwen2.5-Coder-32B | Library enforcement, catches hallucinations |
| **Auditor 1** | Perplexity MCP | Security reasoning |
| **Auditor 2** | Cairo static analysis | Automated scanning |
| **Framework** | OpenHands | Sandboxed agent execution |
| **Security** | OpenZeppelin Cairo v3.0.0 | Audited smart contract library |
| **Infrastructure** | RunPod L40S 48GB | $0.87/hr |
| **Notifications** | Telegram | Human approval for critical decisions |

## 📊 Progress

| Phase | Status | Started | Completed |
|-------|--------|---------|-----------|
| 1. Environment Setup | ✅ Done | Jan 28, 2026 | Jan 28, 2026 |
| 2. Attestation Foundation | 🟡 Active | - | - |
| 3. Relayer Registry | ⚪ Pending | - | - |
| 4. Key Image Tracking | ⚪ Pending | - | - |
| 5. Event Validator | ⚪ Pending | - | - |
| 6. Testing & Audit | ⚪ Pending | - | - |

## 🔴 Live Updates

Follow the build on X: [@oaborunda](https://x.com/oaborunda)

## 📁 Project Structure

```
starknet-monero-agent/
├── AGENTS.md                # AI agent instructions
├── PLAN.md                  # Current agent state
├── README.md                # This file
├── requirements.txt         # Python deps for manager tooling
├── config.toml              # OpenHands configuration
├── system_prompt.md         # Agent instructions
├── launch.py                # Agent launcher
├── .env.template            # Environment template
├── mcp_config.json          # MCP server configuration
├── Makefile                 # Context + validation commands
├── repomix.config.json      # Context generation config
├── context/                 # Repomix outputs (generated)
├── .manager/                # Manager protocol (generated)
│   └── history/.gitkeep
├── docs/
│   ├── architecture.md      # Detailed architecture
│   ├── security.md          # Security decisions log
│   └── decisions/           # ADRs
│       └── 001-oz-only.md
│       └── 002-perplexity-auditor.md
├── scripts/
│   ├── setup-runpod.sh      # Full environment setup
│   ├── launch.sh            # Start agents in tmux
│   ├── manager_sync.py      # Manager sync + research
│   ├── agent_wrapper.sh     # Optional wrapper with reporting
│   └── validate.sh          # Pre-commit validation
├── prompts/                 # Reusable prompt templates
│   ├── architect.md
│   ├── coder.md
│   ├── reviewer.md
│   └── manager.md
└── project/                 # Cairo scaffold (agent-written)
    ├── Scarb.toml
    └── src/
        ├── lib.cairo
        ├── attestation/
        │   ├── event.cairo
        │   ├── quorum_verifier.cairo
        │   └── relayer_registry.cairo
        ├── key_images.cairo
        ├── validator.cairo
        └── utils.cairo
```

## 🔒 Security Approach

| Layer | Protection |
|-------|------------|
| **Foundation** | OpenZeppelin Cairo v3.0.0 (audited) |
| **Constraints** | System prompt forbids custom crypto |
| **Auditor 1** | Perplexity reasoning on patterns |
| **Auditor 2** | Static analysis scanning |
| **Reviewer** | Qwen2.5 enforces library usage |
| **Human** | Telegram approval for critical code |

## ✅ Validation Gates

```bash
make validate
```

This runs the pre-commit checks in `scripts/validate.sh`, including forbidden pattern scans and build/test gates.

## 🚀 Reproduce This Experiment

### Prerequisites
- RunPod account with GPU credits
- L40S 48GB / A100 / RTX 4090
- OpenAI API key
- Perplexity API key

### Quick Start
```bash
# 1. Create RunPod GPU Pod (L40S 48GB, 50GB volume at /workspace)

# 2. Clone and setup
git clone https://github.com/LibreXMR/starknet-monero-agent.git
cd starknet-monero-agent
bash scripts/setup-runpod.sh

# 3. Configure
cp .env.template .env
# Edit .env with your API keys

# 4. Install manager dependencies (if not already installed)
pip install -r requirements.txt

# 5. Generate context + manager guidance (local)
make context
make manager-force

# 6. Launch (RunPod)
bash scripts/launch.sh
```

### Manual Setup
See `docs/architecture.md` for detailed setup instructions.

## 💰 Budget

| Item | Cost | Notes |
|------|------|-------|
| RunPod L40S 48GB | $0.87/hr | ~115 hrs on $100 |
| Perplexity API | ~$5 | Light usage |

## 📈 Why This Matters

1. **Trustless Bridges**: Verify Monero transactions on Starknet without trusted intermediaries
2. **Privacy + Scalability**: Combine Monero's privacy with Starknet's ZK rollup efficiency
3. **AI-Assisted Security**: Dual auditors catch vulnerabilities humans might miss
4. **Reproducible Process**: Fully documented for others to learn and build

## 🤝 Contributing

This is an autonomous AI experiment, but we welcome:
- Security reviews of generated code
- Suggestions for improved agent prompts
- Documentation improvements

## 📜 License

MIT License - Built by AI, verified by humans.

## ⚠️ Disclaimer

This is an experimental project. The generated code should undergo professional security audits before any production use with real funds.

# agent-factory
