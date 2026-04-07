#!/usr/bin/env python3
"""
AI Commit Agent
───────────────
Generates conventional commit messages using OpenAI.
Run via: git agent-commit
"""

import os
import sys
import subprocess
from openai import OpenAI
from dotenv import load_dotenv

# ── Load env from repo root .env ─────────────────────
repo_root = subprocess.run(
    ['git', 'rev-parse', '--show-toplevel'],
    capture_output=True, text=True
).stdout.strip()
load_dotenv(os.path.join(repo_root, '.env'))

# ── Colours for terminal output ──────────────────────
class Color:
    GREEN  = '\033[92m'
    YELLOW = '\033[93m'
    RED    = '\033[91m'
    BLUE   = '\033[94m'
    BOLD   = '\033[1m'
    RESET  = '\033[0m'

def print_step(msg: str):
    print(f"{Color.BLUE}▶ {msg}{Color.RESET}")

def print_success(msg: str):
    print(f"{Color.GREEN}✅ {msg}{Color.RESET}")

def print_warning(msg: str):
    print(f"{Color.YELLOW}⚠️  {msg}{Color.RESET}")

def print_error(msg: str):
    print(f"{Color.RED}❌ {msg}{Color.RESET}")


# ── Get staged diff ───────────────────────────────────
def get_staged_diff() -> str:
    result = subprocess.run(
        ['git', 'diff', '--staged'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()


# ── Get list of staged files ─────────────────────────
def get_staged_files() -> list[str]:
    result = subprocess.run(
        ['git', 'diff', '--staged', '--name-only'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split('\n')


# ── Check if anything is staged ──────────────────────
def has_staged_changes() -> bool:
    result = subprocess.run(
        ['git', 'diff', '--staged', '--quiet'],
        capture_output=True
    )
    return result.returncode != 0


# ── Generate commit message via OpenAI ───────────────
def generate_commit_message(diff: str, files: list[str]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print_error("OPENAI_API_KEY not found in .env file")
        print_warning("Run: cp .env.example .env and add your key")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # Truncate very large diffs to save tokens
    max_diff_chars = 3000
    if len(diff) > max_diff_chars:
        diff = diff[:max_diff_chars] + "\n... [diff truncated]"

    prompt = f"""
You are a senior developer writing git commit messages.

Context: This is a Python FastAPI + Next.js project
for a personalised AI children's storybook service.

Staged files changed:
{chr(10).join(f'  - {f}' for f in files)}

Task: Write ONE conventional commit message for this diff.

Rules:
1. Format: type(scope): description (max 72 chars)
2. Then 2-4 bullet points explaining what + why
3. Types: feat / fix / refactor / docs / test / chore
4. Scope = part of codebase changed (api/story/prompt/
   frontend/config/deps/upload/auth)
5. Description: present tense, no period at end
6. Be specific — no vague messages like "update code"

Return ONLY the commit message.
No explanation. No preamble. Just the message.

Git diff:
{diff}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You write precise git commit messages. Return only the commit message, nothing else."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=200,
        temperature=0.3   # Low temperature = consistent format
    )

    return response.choices[0].message.content.strip()


# ── Run git commit with message ───────────────────────
def run_commit(message: str) -> bool:
    result = subprocess.run(
        ['git', 'commit', '-m', message],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return True
    else:
        print_error(f"Commit failed: {result.stderr}")
        return False


# ── Optional: auto push after commit ─────────────────
def run_push() -> bool:
    result = subprocess.run(
        ['git', 'push'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return True
    else:
        print_warning(f"Push failed: {result.stderr.strip()}")
        return False


# ── Main flow ─────────────────────────────────────────
def main():
    print(f"\n{Color.BOLD}🤖 AI Commit Agent{Color.RESET}")
    print("─" * 40)

    # 1. Check staged changes exist
    if not has_staged_changes():
        print_warning("No staged changes found.")
        print_warning("Run: git add . (or git add <file>)")
        sys.exit(0)

    # 2. Get diff and files
    print_step("Reading staged changes...")
    diff  = get_staged_diff()
    files = get_staged_files()

    print_success(f"Found changes in {len(files)} file(s):")
    for f in files:
        print(f"   📄 {f}")

    # 3. Generate commit message
    print_step("Generating commit message via AI...")
    message = generate_commit_message(diff, files)

    # 4. Show generated message
    print(f"\n{Color.BOLD}📝 Generated Commit Message:{Color.RESET}")
    print("─" * 40)
    print(f"{Color.GREEN}{message}{Color.RESET}")
    print("─" * 40)

    # 5. Ask for confirmation
    print(f"\n{Color.BOLD}Options:{Color.RESET}")
    print("  y  → commit with this message")
    print("  e  → edit message then commit")
    print("  r  → regenerate message")
    print("  n  → cancel")

    choice = input("\nYour choice (y/e/r/n): ").strip().lower()

    if choice == 'y':
        # Commit directly
        if run_commit(message):
            print_success("Committed successfully!")

            # Ask about push
            push_choice = input("\nPush to remote? (y/n): ").strip().lower()
            if push_choice == 'y':
                if run_push():
                    print_success("Pushed to remote!")
                else:
                    print_warning("Push failed — try manually: git push")

    elif choice == 'e':
        # Let user edit the message
        print(f"\nEdit the message below (press Enter when done):")
        print(f"Current: {message}")
        edited = input("New message: ").strip()
        if edited:
            if run_commit(edited):
                print_success(f"Committed with your message!")
        else:
            print_warning("Empty message — commit cancelled")

    elif choice == 'r':
        # Regenerate
        print_step("Regenerating...")
        new_message = generate_commit_message(diff, files)
        print(f"\n{Color.BOLD}📝 New Message:{Color.RESET}")
        print(f"{Color.GREEN}{new_message}{Color.RESET}")
        confirm = input("\nCommit with this? (y/n): ").strip().lower()
        if confirm == 'y':
            if run_commit(new_message):
                print_success("Committed!")

    else:
        print_warning("Commit cancelled.")

    print()


if __name__ == "__main__":
    main()