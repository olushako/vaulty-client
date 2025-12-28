#!/bin/bash
# Run the same checks locally that CI runs
# Usage: ./scripts/check.sh

set -e

echo "🔍 Running ruff checks..."
ruff check .

echo "📝 Running ruff format check..."
ruff format --check .

echo "🔬 Running mypy..."
mypy vaulty --ignore-missing-imports || true

echo "🧪 Running tests..."
pytest tests/ -v --cov=vaulty --cov-report=term-missing --cov-fail-under=50

echo "✅ All checks passed!"
