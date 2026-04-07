#!/usr/bin/env python3
"""
AI Standup Generator
─────────────────────
Reads yesterday's commits → generates standup update.
Run via: git standup
"""

import os
import sys
import subprocess
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_yesterdays_commits() -> str:
    yesterday = (
        datetime.now() - timedelta(days=1)
    ).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")

    result = subprocess.run([
        'git', 'log',
        f'--after={yesterday} 00:00',
        f'--before={today} 23:59',
        '--pretty=format:%s',
        '--no-merges',
        '--all'
    ], capture_output=True, text=True)

    return result.stdout.strip()


def get_current_branch() -> str:
    result = subprocess.run(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def generate_standup(
    commits: str,
    branch: str
) -> str:
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    prompt = f"""
ROLE:
You are a senior developer writing a daily standup
update for a Slack/Teams channel.

CONTEXT:
Developer: Tech Lead on a Python FastAPI +
Next.js project.
Current branch: {branch}
Yesterday's commits:
{commits if commits else "No commits found"}

TASK:
Write a concise standup update covering:
1. What was completed yesterday
2. What is planned for today
3. Any blockers (say "None" if not obvious)

RULES:
- Max 5 lines total
- Use bullet points
- Professional but conversational
- Infer "today's plan" from the branch name
  and what's logically next after yesterday
- Never say "worked on stuff" — be specific

FORMAT:
**Yesterday:**
- [specific thing done]
- [specific thing done]

**Today:**
- [specific plan]
- [specific plan]

**Blockers:** None
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Write concise developer standups. Be specific. Max 5 lines."
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        temperature=0.3
    )

    return response.choices[0].message.content.strip()


def main():
    print("\n🎯 AI Standup Generator")
    print("─" * 35)

    branch  = get_current_branch()
    commits = get_yesterdays_commits()

    if not commits:
        print("⚠️  No commits found from yesterday.")
        print("Generating based on branch name only...")

    print(f"📌 Branch: {branch}")
    if commits:
        print("📝 Yesterday's commits found:")
        for c in commits.split('\n')[:5]:
            print(f"   • {c}")

    print("\n⏳ Generating standup...")
    standup = generate_standup(commits, branch)

    print("\n" + "─" * 35)
    print("📋 YOUR STANDUP:")
    print("─" * 35)
    print(standup)
    print("─" * 35)

    # Copy to clipboard
    try:
        subprocess.run(
            ['pbcopy'],
            input=standup.encode(),
            check=True
        )
        print("\n✅ Copied to clipboard!")
        print("   Paste directly into Slack/Teams")
    except:
        print("\n💡 Copy the standup above")

    print()


if __name__ == "__main__":
    main()