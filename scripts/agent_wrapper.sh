#!/bin/bash
# Wrapper that runs an agent action and handles manager protocol

set -euo pipefail

MANAGER_DIR=".manager"
CALL_COUNT_FILE="$MANAGER_DIR/call_count"
REPORT_FILE="$MANAGER_DIR/report.md"
GUIDANCE_FILE="$MANAGER_DIR/guidance.md"

# Ensure directories exist
mkdir -p "$MANAGER_DIR"

# Function to increment call count
increment_count() {
    local count
    count=$(cat "$CALL_COUNT_FILE" 2>/dev/null || echo 0)
    echo $((count + 1)) > "$CALL_COUNT_FILE"
    echo "📊 Call count: $((count + 1))"
}

# Function to check if manager sync needed
check_manager() {
    local count
    count=$(cat "$CALL_COUNT_FILE" 2>/dev/null || echo 0)
    if [ "$count" -ge 3 ]; then
        echo "🧠 Call threshold reached. Triggering manager sync..."
        python scripts/manager_sync.py --force
        return 0
    fi
    return 1
}

# Function to append to report
append_report() {
    local agent="$1"
    local action="$2"
    local result="$3"
    local files="${4:-"(not captured)"}"
    local next="${5:-"(see guidance)"}"
    local stuck="${6:-"No"}"

    {
        echo ""
        echo "## $(date '+%Y-%m-%d %H:%M:%S') - $agent"
        echo "**Action**: $action"
        echo "**Files**: $files"
        echo "**Result**: $result"
        echo "**Next**: $next"
        echo "**Stuck**: $stuck"
        echo ""
    } >> "$REPORT_FILE"
}

# Main: Check guidance exists
if [ ! -f "$GUIDANCE_FILE" ]; then
    echo "⚠️ No guidance file. Running initial manager sync..."
    python scripts/manager_sync.py --force || true
fi

# Show current guidance summary
echo "📋 Current guidance available at: $GUIDANCE_FILE"
echo "📊 Current call count: $(cat "$CALL_COUNT_FILE" 2>/dev/null || echo 0)"

# If arguments provided, run them as a command
if [ $# -gt 0 ]; then
    echo "🚀 Running: $*"
    set +e
    "$@"
    exit_code=$?
    set -e

    if [ "$exit_code" -eq 0 ]; then
        append_report "Agent" "$*" "Success"
    else
        append_report "Agent" "$*" "Failed (exit code $exit_code)"
    fi

    increment_count
    check_manager || true

    exit "$exit_code"
fi
