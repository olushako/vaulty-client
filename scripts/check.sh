#!/bin/bash
# Run the same checks locally that CI runs
# Usage: ./scripts/check.sh

set -e

echo "🔍 Running ruff checks and auto-fixing..."
ruff check . --fix

echo "📝 Running ruff format..."
ruff format .

echo "🔬 Running mypy (non-blocking)..."
mypy vaulty --ignore-missing-imports || echo "⚠️  Mypy found type errors (non-blocking)"

echo "🧪 Running tests..."
pytest tests/ -v --cov=vaulty --cov-report=term-missing --cov-fail-under=50

echo "✅ All checks passed!"
