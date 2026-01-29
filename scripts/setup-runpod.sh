#!/bin/bash
# ============================================
# Starknet Monero Agent - RunPod Setup Script
# ============================================
# Requirements:
# - RunPod GPU Pod (L40S 48GB / A100 / RTX 4090)
# - 50GB+ persistent storage at /workspace
#
# Usage: bash scripts/setup-runpod.sh
# ============================================

set -e

echo "🚀 Starting Starknet Monero Agent Setup..."
echo "============================================"

# Step 1: Install system dependencies
echo "📦 Installing system dependencies..."
apt-get update
apt-get install -y zstd python3.11 python3.11-venv python3-pip git tmux curl nodejs npm jq

# Step 2: Install Ollama
echo "🦙 Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Step 3: Configure Ollama to use persistent storage
echo "💾 Configuring Ollama storage..."
mkdir -p /workspace/ollama /workspace/logs
export OLLAMA_MODELS=/workspace/ollama
echo 'export OLLAMA_MODELS=/workspace/ollama' >> ~/.bashrc

# Step 4: Start Ollama server
echo "🔧 Starting Ollama server..."
ollama serve > /workspace/logs/ollama.log 2>&1 &
sleep 5

# Step 5: Download models
echo "📥 Downloading GLM-4.7-Flash (~19GB, ~15 min)..."
ollama pull glm-4.7-flash

echo "📥 Downloading Qwen2.5-Coder-32B (~19GB, ~10 min)..."
ollama pull qwen2.5-coder:32b

# Step 6: Verify models
echo "✅ Installed models:"
ollama list

# Step 7: Install Python dependencies
echo "🐍 Setting up Python environment..."
python3.11 -m venv /workspace/starknet-monero-agent/venv
source /workspace/starknet-monero-agent/venv/bin/activate
pip install --upgrade pip
pip install openhands-ai litellm aiohttp pydantic python-dotenv
pip install -r /workspace/starknet-monero-agent/requirements.txt

# Step 8: Install MCP tools
echo "🔌 Installing MCP servers..."
npm install -g @anthropic/mcp-server-perplexity
npm install -g cairo-coder-mcp openzeppelin-cairo-mcp
npm install -g agent-reachout-mcp

# Step 9: Install Cairo/Scarb toolchain
echo "🏗️ Installing Cairo toolchain..."
curl --proto '=https' --tlsv1.2 -sSf https://docs.swmansion.com/scarb/install.sh | sh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Step 10: Install Starknet Foundry
echo "🔨 Installing Starknet Foundry..."
curl -L https://raw.githubusercontent.com/foundry-rs/starknet-foundry/master/scripts/install.sh | sh

echo "============================================"
echo "✅ Setup complete!"
echo ""
echo "📊 GPU Status:"
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv
echo ""
echo "🦙 Models installed:"
ollama list
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. cp .env.template .env"
echo "  2. Edit .env with your API keys"
echo "  3. bash scripts/launch.sh"
echo "============================================"
