#!/bin/bash
# ═══════════════════════════════════════════════════
# AI Dev Tools Setup Script
# Run this once to set up AI tools for the team
# Usage: bash scripts/setup_ai_tools.sh
# ═══════════════════════════════════════════════════

echo ""
echo "🤖 Setting up AI Dev Tools..."
echo "─────────────────────────────"

# ── Check Python is installed ─────────────────────
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.10+"
    exit 1
fi
echo "✅ Python3 found: $(python3 --version)"

# ── Check pip ─────────────────────────────────────
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found."
    exit 1
fi

# ── Install required packages ─────────────────────
echo "▶ Installing required packages..."
pip3 install openai python-dotenv --quiet
echo "✅ Packages installed"

# ── Set up .env if not exists ─────────────────────
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env created from .env.example"
    echo "⚠️  Add your OPENAI_API_KEY to .env file"
else
    echo "✅ .env already exists"
fi

# ── Install git agent-commit command ──────────────
echo "▶ Installing git agent-commit command..."

SCRIPT_PATH="$(pwd)/scripts/ai_commit.py"

if [ "$(uname)" == "Darwin" ] || [ "$(uname)" == "Linux" ]; then
    # Mac or Linux
    sudo cp "$SCRIPT_PATH" /usr/local/bin/git-agent-commit
    sudo chmod +x /usr/local/bin/git-agent-commit
    echo "✅ git agent-commit installed (Mac/Linux)"
else
    # Windows — add to PATH via git config
    git config --global alias.agent-commit \
        "!python3 $(pwd)/scripts/ai_commit.py"
    echo "✅ git agent-commit installed (Windows via alias)"
fi

# ── Verify installation ───────────────────────────
echo ""
echo "─────────────────────────────"
echo "✅ Setup complete!"
echo ""
echo "How to use:"
echo "  1. Stage your changes:  git add ."
echo "  2. Run AI commit:       git agent-commit"
echo "  3. Or via VS Code:      Ctrl+Shift+P → Run Task → AI Commit Agent"
echo ""
echo "⚠️  Make sure OPENAI_API_KEY is set in your .env file"
echo "─────────────────────────────"

# ── Install git agent-pr command ──────────────────────
echo "▶ Installing git agent-pr command..."
PR_SCRIPT_PATH="$(pwd)/scripts/ai_pr.py"

if [ "$(uname)" == "Darwin" ] || \
   [ "$(uname)" == "Linux" ]; then
    sudo cp "$PR_SCRIPT_PATH" \
        /usr/local/bin/git-agent-pr
    sudo chmod +x /usr/local/bin/git-agent-pr
    echo "✅ git agent-pr installed (Mac/Linux)"
else
    git config --global alias.agent-pr \
        "!python3 $(pwd)/scripts/ai_pr.py"
    echo "✅ git agent-pr installed (Windows)"
fi

echo ""
echo "AI Tools installed:"
echo "  git agent-commit → AI commit messages"
echo "  git agent-pr     → AI PR descriptions"