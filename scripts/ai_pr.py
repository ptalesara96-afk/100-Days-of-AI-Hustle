#!/usr/bin/env python3
"""
AI PR Description Generator
────────────────────────────
Generates professional PR descriptions using OpenAI.
Run via: git agent-pr
"""

import os
import sys
import subprocess
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class Color:
    GREEN  = '\033[92m'
    YELLOW = '\033[93m'
    RED    = '\033[91m'
    BLUE   = '\033[94m'
    BOLD   = '\033[1m'
    RESET  = '\033[0m'

def run_command(cmd: list[str]) -> str:
    result = subprocess.run(
        cmd, capture_output=True, text=True
    )
    return result.stdout.strip()


def get_branch_name() -> str:
    return run_command(['git', 'rev-parse',
                       '--abbrev-ref', 'HEAD'])


def get_commits_since_main() -> str:
    return run_command([
        'git', 'log', 'main..HEAD',
        '--pretty=format:%s', '--no-merges'
    ])


def get_diff_since_main() -> str:
    diff = run_command(['git', 'diff', 'main..HEAD'])
    # Truncate large diffs
    return diff[:4000] + "\n...[truncated]" \
        if len(diff) > 4000 else diff


def get_files_changed() -> str:
    return run_command([
        'git', 'diff', 'main..HEAD', '--name-only'
    ])


def generate_pr_description(
    branch: str,
    commits: str,
    diff: str,
    files: str
) -> str:

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(f"{Color.RED}❌ OPENAI_API_KEY not found{Color.RESET}")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    prompt = f"""
ROLE:
You are a senior developer writing a GitHub Pull Request
description. Your PR descriptions are clear, complete,
and help reviewers understand changes in under 2 minutes.

CONTEXT:
Project: Python FastAPI + Next.js children's storybook
service. Team is mid-level. PRs go through code review
before merging to main.

Branch name: {branch}

Commits in this PR:
{commits}

Files changed:
{files}

FEW-SHOT EXAMPLE — Write in this exact format:

## What This PR Does
Adds Pydantic validation to the story generation endpoint
to reject invalid input before hitting the OpenAI API.

## Why
Without validation, invalid age values (e.g. "five")
caused silent 500 crashes. Parents submitting the form
got no error feedback.

## Changes Made
- `api/main.py` — Add StoryRequestBody Pydantic model
- `api/main.py` — Add @validator for child_name field
- `tests/test_api.py` — Add 5 validation test cases

## How To Test
1. Run: uvicorn api.main:app --reload
2. POST /generate-story with age: "abc"
3. Expect: 422 with message "value is not a valid integer"

## Screenshots / Output
[Add terminal output or Postman screenshot if relevant]

## Checklist
- [x] Tested locally
- [x] No breaking changes
- [ ] Docs updated (if needed)

(End of example — now write the PR description below)

TASK:
Write a complete PR description for this branch.
Match the format and specificity of the example exactly.
Be specific about file names and what changed in each.

Git diff:
{diff}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You write precise GitHub PR descriptions. Return only the PR description in markdown. No preamble."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=600,
        temperature=0.3
    )

    return response.choices[0].message.content.strip()


def copy_to_clipboard(text: str):
    try:
        # Mac
        subprocess.run(['pbcopy'],
            input=text.encode(), check=True)
        return True
    except:
        try:
            # Linux
            subprocess.run(['xclip', '-selection',
                'clipboard'],
                input=text.encode(), check=True)
            return True
        except:
            return False


def main():
    print(f"\n{Color.BOLD}🚀 AI PR Description Generator"
          f"{Color.RESET}")
    print("─" * 45)

    # Get branch info
    branch = get_branch_name()

    if branch == 'main':
        print(f"{Color.YELLOW}⚠️  You're on main branch.")
        print(f"Create a feature branch first:"
              f"{Color.RESET}")
        print(f"git checkout -b feat/your-feature-name")
        sys.exit(0)

    print(f"{Color.BLUE}▶ Branch: {branch}{Color.RESET}")

    # Get commits
    commits = get_commits_since_main()
    if not commits:
        print(f"{Color.YELLOW}⚠️  No commits ahead of main."
              f"{Color.RESET}")
        sys.exit(0)

    commit_lines = commits.split('\n')
    print(f"{Color.BLUE}▶ Commits: "
          f"{len(commit_lines)}{Color.RESET}")
    for c in commit_lines:
        print(f"   • {c}")

    # Get files + diff
    files = get_files_changed()
    diff  = get_diff_since_main()

    # Generate description
    print(f"\n{Color.BLUE}▶ Generating PR description..."
          f"{Color.RESET}")
    description = generate_pr_description(
        branch, commits, diff, files
    )

    # Display
    print(f"\n{Color.BOLD}📋 Generated PR Description:"
          f"{Color.RESET}")
    print("─" * 45)
    print(f"{Color.GREEN}{description}{Color.RESET}")
    print("─" * 45)

    # Options
    print(f"\n{Color.BOLD}Options:{Color.RESET}")
    print("  y → copy to clipboard + open GitHub")
    print("  p → just print (already done)")
    print("  n → cancel")

    choice = input("\nYour choice (y/p/n): ").strip().lower()

    if choice == 'y':
        copied = copy_to_clipboard(description)
        if copied:
            print(f"{Color.GREEN}✅ Copied to clipboard!"
                  f"{Color.RESET}")

        # Open GitHub PR page
        remote = run_command([
            'git', 'remote', 'get-url', 'origin'
        ])
        if 'github.com' in remote:
            repo = remote.replace(
                'git@github.com:', ''
            ).replace(
                'https://github.com/', ''
            ).replace('.git', '')

            pr_url = (f"https://github.com/{repo}"
                     f"/compare/{branch}?expand=1")
            subprocess.run(['open', pr_url])
            print(f"{Color.GREEN}✅ GitHub PR page opened!"
                  f"{Color.RESET}")
            print(f"{Color.YELLOW}   Paste description "
                  f"from clipboard{Color.RESET}")

    print()


if __name__ == "__main__":
    main()