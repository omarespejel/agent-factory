#!/usr/bin/env python3
"""
Starknet Monero Light Client - Autonomous Agent Launcher
"""

import asyncio
import os
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent
SYSTEM_PROMPT = (ROOT / "system_prompt.md").read_text()
MANAGER_DIR = ROOT / ".manager"
GUIDANCE_FILE = MANAGER_DIR / "guidance.md"
CALL_COUNT_FILE = MANAGER_DIR / "call_count"

MCP_GATES = """
## Mandatory MCP + Build/Test Gates (Do Not Skip)

1. Before any Cairo code change, call **Cairo Coder MCP** with the exact task.
2. Before using contract patterns, access control, or security components, call **OpenZeppelin MCP**.
3. After every Cairo edit, run `scarb build` and `snforge test`.
4. If any gate fails, stop and fix before proceeding.
"""

INITIAL_TASK = """
## PHASE 1: Attestation Foundation

**IMPORTANT:** Read `docs/spec/monero-verification.md` first.
We are implementing Approach A: Quorum Attestation.

### Step 1: Research (Use Perplexity)
Query: "threshold signature verification patterns Cairo Starknet production"
Query: "ECDSA signature aggregation Cairo OpenZeppelin"

### Step 2: Define MoneroEventV1 Schema
Create `src/attestation/event.cairo` with:
- Canonical event struct
- Domain-separated hash function (spec-guided)

### Step 3: Design Quorum Verifier Interface
Create `src/attestation/quorum_verifier.cairo` with:
- Trait for threshold signature verification
- Storage for authorized relayers
- Threshold parameter

### Step 4: Write Tests First
Create tests for:
- Event hash computation
- Single signature verification
- Threshold verification (2-of-3, 3-of-5)

### Step 5: Implement
- Use OZ ECDSA verification if available
- Follow threshold patterns from Perplexity research

### Step 6: Commit
Commit: "feat: MoneroEventV1 schema and quorum verifier foundation"

After Phase 1, proceed to Phase 2: Relayer Registry.
"""

TASK = f"{MCP_GATES}\n{INITIAL_TASK}"


def preflight_or_exit() -> None:
    strict = os.getenv("OPENHANDS_PREFLIGHT_STRICT", "1") != "0"
    missing = [tool for tool in ("scarb", "snforge") if shutil.which(tool) is None]
    if missing:
        message = f"Missing required tools: {', '.join(missing)}"
        if strict:
            print(f"❌ {message}")
            print("Install them or set OPENHANDS_PREFLIGHT_STRICT=0 to bypass.")
            sys.exit(1)
        print(f"⚠️ {message}")
    workspace_base = Path("/workspace/starknet-monero-agent/project")
    if not workspace_base.exists():
        workspace_base.mkdir(parents=True, exist_ok=True)

def ensure_manager_setup() -> None:
    """Ensure manager directory and guidance exist."""
    MANAGER_DIR.mkdir(exist_ok=True)

    if not GUIDANCE_FILE.exists():
        print("🧠 No guidance found. Running initial manager sync...")
        result = subprocess.run(
            ["python", "scripts/manager_sync.py", "--force"],
            cwd=ROOT,
        )
        if result.returncode != 0:
            print("⚠️ Manager sync failed. Using default guidance.")
            GUIDANCE_FILE.write_text(
                "# Initial Guidance\n\n"
                "No manager sync available. Follow the PLAN.md and system_prompt.md.\n\n"
                "## Next Steps\n"
                "1. Read `docs/spec/monero-verification.md`\n"
                "2. Check current phase in `PLAN.md`\n"
                "3. Implement next TODO item\n"
                "4. Run `make build test` after changes\n"
            )


def get_call_count() -> int:
    """Get current call count."""
    if CALL_COUNT_FILE.exists():
        try:
            return int(CALL_COUNT_FILE.read_text().strip())
        except ValueError:
            return 0
    return 0


def print_manager_status() -> None:
    """Print manager status summary."""
    print("=" * 60)
    print("MANAGER STATUS")
    print("=" * 60)
    print(f"📊 Call count: {get_call_count()}/3")
    print(f"📋 Guidance: {GUIDANCE_FILE}")
    print("=" * 60)


def print_guidance_preview() -> None:
    """Print the current guidance (truncated)."""
    if GUIDANCE_FILE.exists():
        guidance = GUIDANCE_FILE.read_text()
        print("\n📋 CURRENT MANAGER GUIDANCE:")
        print("-" * 60)
        if len(guidance) > 2000:
            print(guidance[:2000] + "\n\n[... truncated, see full file ...]")
        else:
            print(guidance)
        print("-" * 60)


async def main() -> None:
    print("=" * 60)
    print("🚀 Starknet Monero Light Client - Autonomous Build")
    print("=" * 60)
    print("Primary Coder:  GLM-4.7-Flash (fast, tool calling)")
    print("Reviewer:       Qwen2.5-Coder-32B (library enforcement)")
    print("Auditor:        Perplexity MCP (security reasoning)")
    print("=" * 60)

    ensure_manager_setup()
    print_manager_status()
    print_guidance_preview()

    preflight_or_exit()

    try:
        from openhands.core.config import load_config
        from openhands.core.main import run_agent

        config = load_config("config.toml")

        await run_agent(
            task=TASK,
            system_prompt=SYSTEM_PROMPT,
            config=config,
        )
    except ImportError:
        print("⚠️ OpenHands not fully installed. Running in test mode...")
        print("\nSystem Prompt loaded:")
        print(SYSTEM_PROMPT[:500] + "...")
        print("\nInitial Task:")
        print(INITIAL_TASK)


if __name__ == "__main__":
    asyncio.run(main())
