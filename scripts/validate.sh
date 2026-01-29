#!/usr/bin/env bash
set -euo pipefail

echo "🔍 Validating agent changes..."

PROJECT_DIR="project/src"
if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "❌ Missing $PROJECT_DIR"
  exit 1
fi

# Check for forbidden patterns
if grep -R -n -E "impl.*(ec_|ec_point|hash|random)" "$PROJECT_DIR"; then
  echo "❌ BLOCKED: Custom crypto detected"
  exit 1
fi

# Check for unresolved human review tags
if grep -R -n "NEEDS_HUMAN_REVIEW" "$PROJECT_DIR"; then
  echo "⚠️ WARNING: Unresolved NEEDS_HUMAN_REVIEW tags found"
fi

# Verify OZ imports present
if ! grep -R -n -E "use openzeppelin" "$PROJECT_DIR"/*.cairo >/dev/null 2>&1; then
  echo "⚠️ WARNING: No OpenZeppelin imports found"
fi

# Build and test
cd project
scarb build
snforge test

echo "✅ Validation passed"
