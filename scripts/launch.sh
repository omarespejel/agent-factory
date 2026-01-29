#!/bin/bash
# ============================================
# Starknet Monero Agent - Launch Script
# ============================================

set -e

cd /workspace/starknet-monero-agent

# Ensure workspace exists for agent runs
mkdir -p /workspace/starknet-monero-agent/project

# Preflight tools
for tool in scarb snforge; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "❌ Missing required tool: $tool"
        echo "Install it or set OPENHANDS_PREFLIGHT_STRICT=0 before launch."
        exit 1
    fi
done

# Load environment
source venv/bin/activate
source .env 2>/dev/null || echo "⚠️ No .env file found"

# Ensure Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "🦙 Starting Ollama server..."
    export OLLAMA_MODELS=/workspace/ollama
    ollama serve > /workspace/logs/ollama.log 2>&1 &
    sleep 5
fi

# Verify models are available
echo "📋 Available models:"
ollama list

# Start in tmux for persistence
echo "🚀 Launching agent in tmux session 'agent'..."
echo "   - Detach: Ctrl+B then D"
echo "   - Reattach: tmux attach -t agent"
echo ""

tmux new-session -d -s agent "cd /workspace/starknet-monero-agent && source venv/bin/activate && python launch.py"
tmux attach -t agent
