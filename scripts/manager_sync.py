#!/usr/bin/env python3
"""
Manager Sync: Orchestrates GPT-5.2-Codex as the manager agent.
Also integrates Perplexity for web-grounded research queries.

Usage:
    python scripts/manager_sync.py           # Full manager sync
    python scripts/manager_sync.py --check   # Check if sync needed
    python scripts/manager_sync.py --force   # Force sync regardless of count
    python scripts/manager_sync.py --research "query"  # Perplexity research
    python scripts/manager_sync.py --increment          # Increment call count
    python scripts/manager_sync.py --reset              # Reset call count
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # optional dependency
    load_dotenv = None

try:
    import openai
except ImportError:
    print("❌ openai package required: pip install openai")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("❌ requests package required: pip install requests")
    sys.exit(1)

# Paths
ROOT = Path(__file__).parent.parent
MANAGER_DIR = ROOT / ".manager"
CONTEXT_FILE = ROOT / "context" / "context.xml"
GUIDANCE_FILE = MANAGER_DIR / "guidance.md"
REPORT_FILE = MANAGER_DIR / "report.md"
CALL_COUNT_FILE = MANAGER_DIR / "call_count"
HISTORY_DIR = MANAGER_DIR / "history"
STATE_FILE = MANAGER_DIR / "state.json"
PROMPT_FILE = ROOT / "prompts" / "manager.md"
REPOMIX_CONFIG = ROOT / "repomix.config.json"

# Config
CALL_THRESHOLD = int(os.getenv("MANAGER_CALL_THRESHOLD", "3"))
MAX_CONTEXT_CHARS = int(os.getenv("MANAGER_MAX_CONTEXT_CHARS", "300000"))
MANAGER_MODEL = os.getenv("MANAGER_MODEL", "gpt-5.2-codex")
MANAGER_REASONING = os.getenv("MANAGER_REASONING", "high")
MANAGER_MAX_TOKENS = int(os.getenv("MANAGER_MAX_TOKENS", "16000"))
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-reasoning-pro")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def ensure_dirs() -> None:
    """Create manager directories if they don't exist."""
    MANAGER_DIR.mkdir(exist_ok=True)
    HISTORY_DIR.mkdir(exist_ok=True)


def get_call_count() -> int:
    """Get current call count."""
    if CALL_COUNT_FILE.exists():
        try:
            return int(CALL_COUNT_FILE.read_text().strip())
        except ValueError:
            return 0
    return 0


def increment_call_count() -> int:
    """Increment and return new call count."""
    count = get_call_count() + 1
    CALL_COUNT_FILE.write_text(str(count))
    return count


def reset_call_count() -> None:
    """Reset call count to 0."""
    CALL_COUNT_FILE.write_text("0")


def get_state() -> dict:
    """Get manager state."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_sync": None, "total_syncs": 0, "stuck_count": 0}


def save_state(state: dict) -> None:
    """Save manager state."""
    STATE_FILE.write_text(json.dumps(state, indent=2))


def timestamp() -> str:
    """Get current timestamp string."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def load_prompt() -> str:
    """Load manager system prompt."""
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text()
    return (
        "You are the Manager Agent for a Starknet Monero light client project.\n"
        "Provide architectural guidance, unblock agents, and flag security risks.\n"
    )


def run_repomix() -> None:
    """Run repomix with repository config."""
    if not REPOMIX_CONFIG.exists():
        raise FileNotFoundError("repomix.config.json not found")
    ensure_dirs()
    cmd = ["repomix", "--config", str(REPOMIX_CONFIG)]
    if shutil.which("repomix") is None:
        cmd = ["npx", "repomix", "--config", str(REPOMIX_CONFIG)]
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        raise RuntimeError("repomix failed")


def generate_context() -> str:
    """Generate fresh context using repomix."""
    print("📦 Generating context with repomix...")
    run_repomix()
    if CONTEXT_FILE.exists():
        content = CONTEXT_FILE.read_text()
        if len(content) > MAX_CONTEXT_CHARS:
            print(
                f"⚠️ Context truncated for prompt "
                f"({len(content)} -> {MAX_CONTEXT_CHARS} chars)"
            )
            return content[:MAX_CONTEXT_CHARS] + "\n\n[TRUNCATED]"
        return content
    return ""


# ============================================================================
# GPT-5.2-CODEX MANAGER
# ============================================================================


def call_codex_manager(context: str, report: str) -> str:
    """Call GPT-5.2-Codex with thinking high."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    client = openai.OpenAI(api_key=api_key)

    user_message = f"""## FULL CODEBASE CONTEXT
{context}

## AGENT PROGRESS REPORT
{report if report else "No report. This is a periodic check or fresh start."}

## YOUR TASK
Analyze the codebase and provide guidance for the next development cycle.
Focus on what's most important RIGHT NOW."""

    print("🧠 Calling manager model...")

    response = client.chat.completions.create(
        model=MANAGER_MODEL,
        reasoning_effort=MANAGER_REASONING,
        max_completion_tokens=MANAGER_MAX_TOKENS,
        messages=[
            {"role": "system", "content": load_prompt()},
            {"role": "user", "content": user_message},
        ],
    )

    return response.choices[0].message.content


# ============================================================================
# PERPLEXITY RESEARCH
# ============================================================================


def call_perplexity_research(query: str, context: str = "") -> str:
    """Call Perplexity for web-grounded research."""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY not set")

    print(f"🔍 Researching with Perplexity: {query[:60]}...")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a security-focused research assistant for a Cairo/Starknet project.\n"
                "Provide answers with citations. Focus on:\n"
                "- Production-grade patterns\n"
                "- Audited implementations\n"
                "- Known vulnerabilities\n"
                "- Best practices from audited codebases"
            ),
        },
        {
            "role": "user",
            "content": f"{query}\n\nContext (if relevant):\n"
            f"{context[:10000] if context else 'None'}",
        },
    ]

    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": PERPLEXITY_MODEL,
            "messages": messages,
            "max_tokens": 4000,
        },
        timeout=120,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Perplexity API error: {response.status_code} - {response.text}"
        )

    return response.json()["choices"][0]["message"]["content"]


# ============================================================================
# MAIN SYNC LOGIC
# ============================================================================


def sync(force: bool = False) -> str:
    """Main sync: generate context, call manager, save guidance."""
    ensure_dirs()

    # Check if sync needed
    count = get_call_count()
    if not force and count < CALL_THRESHOLD:
        print(
            f"ℹ️ Call count {count}/{CALL_THRESHOLD}. "
            "Use --force to sync anyway."
        )
        return ""

    # 1. Generate fresh context
    context = generate_context()
    if not context:
        print("❌ Failed to generate context")
        return ""

    # 2. Read agent report
    report = REPORT_FILE.read_text() if REPORT_FILE.exists() else ""

    # 3. Call manager
    try:
        guidance = call_codex_manager(context, report)
    except Exception as exc:
        print(f"❌ Manager call failed: {exc}")
        return ""

    # 4. Save guidance
    GUIDANCE_FILE.write_text(guidance)
    print(f"✅ Guidance saved to {GUIDANCE_FILE}")

    # 5. Archive
    ts = timestamp()
    archive_file = HISTORY_DIR / f"{ts}.md"
    archive_content = f"""# Manager Guidance - {ts}

## Report Received
{report if report else "(none)"}

## Guidance Provided
{guidance}
"""
    archive_file.write_text(archive_content)

    # 6. Update state
    state = get_state()
    state["last_sync"] = ts
    state["total_syncs"] = state.get("total_syncs", 0) + 1
    save_state(state)

    # 7. Reset counter and report
    reset_call_count()
    REPORT_FILE.write_text("")

    print(f"📁 Archived to {archive_file}")
    print(f"🔄 Call count reset. Total syncs: {state['total_syncs']}")

    return guidance


def check_needed() -> bool:
    """Check if manager sync is needed."""
    count = get_call_count()
    needed = count >= CALL_THRESHOLD
    print(f"📊 Call count: {count}/{CALL_THRESHOLD}")
    print("🟢 Sync needed" if needed else "🟡 Not yet needed")
    return needed


# ============================================================================
# CLI
# ============================================================================


def main() -> None:
    if load_dotenv is not None:
        load_dotenv()

    parser = argparse.ArgumentParser(
        description="Manager sync for Starknet Monero project"
    )
    parser.add_argument("--check", action="store_true", help="Check if sync needed")
    parser.add_argument("--force", action="store_true", help="Force sync regardless")
    parser.add_argument("--research", type=str, help="Run Perplexity research query")
    parser.add_argument(
        "--increment", action="store_true", help="Increment call count"
    )
    parser.add_argument("--reset", action="store_true", help="Reset call count")

    args = parser.parse_args()

    if args.check:
        check_needed()
    elif args.research:
        ensure_dirs()
        context = CONTEXT_FILE.read_text() if CONTEXT_FILE.exists() else ""
        result = call_perplexity_research(args.research, context)
        print("\n" + "=" * 60)
        print(result)
        print("=" * 60)
    elif args.increment:
        new_count = increment_call_count()
        print(f"📊 Call count: {new_count}")
        if new_count >= CALL_THRESHOLD:
            print("🟢 Threshold reached! Run sync.")
    elif args.reset:
        reset_call_count()
        print("🔄 Call count reset to 0")
    else:
        sync(force=args.force)


if __name__ == "__main__":
    main()
