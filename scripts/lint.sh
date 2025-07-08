#!/bin/bash
# Code quality checking script for local development

set -e

echo "🔍 Running code quality checks..."

echo "📦 Installing/updating dev dependencies..."
pip install -r requirements-dev.txt

echo "🎨 Formatting code with black..."
black src/ tests/ --line-length 100  # Format first
isort src/ tests/                    # Sort imports

echo "📋 Sorting imports with isort..."
isort src/ tests/ --check-only --diff

echo "🔍 Linting with flake8..."
flake8 src/ tests/

echo "🔍 Type checking with mypy..."
mypy src/ --ignore-missing-imports --no-strict-optional

echo "🔒 Security scanning with bandit..."
bandit -r src/ -f screen

echo "🧪 Running tests..."
python -m pytest tests/ -v --cov=src --cov-report=term-missing

echo "✅ All quality checks passed!"
