#!/bin/bash
# Run the same checks locally that CI runs
# Usage: ./scripts/check.sh

set -e

echo "🔍 Running ruff check (matching CI - no auto-fix)..."
if ! ruff check .; then
    echo "❌ Ruff check failed! Fix errors manually or run: ruff check . --fix"
    exit 1
fi

echo "📝 Running ruff format check (matching CI)..."
if ! ruff format --check .; then
    echo "❌ Ruff format check failed! Fix formatting with: ruff format ."
    exit 1
fi

echo "🔬 Running mypy (matching CI)..."
mypy vaulty --ignore-missing-imports || echo "⚠️  Mypy found type errors (non-blocking)"

echo "🧪 Running tests..."
pytest tests/ -v --cov=vaulty --cov-report=term-missing --cov-fail-under=50

echo "✅ All checks passed!"
