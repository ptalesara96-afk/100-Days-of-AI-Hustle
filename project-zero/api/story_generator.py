import os
from openai import OpenAI
from dotenv import load_dotenv
from dataclasses import dataclass

# Load environment variables from .env file
load_dotenv()


# ── Data shape for story input ──────────────────────────
@dataclass
class StoryRequest:
    child_name: str
    age: int
    theme: str              # e.g. "space adventure"
    favourite_thing: str    # e.g. "dinosaurs"


# ── 4-Layer prompt — same framework, different model ────
def build_story_prompt(request: StoryRequest) -> str:
    return f"""
ROLE:
You are a warm, imaginative children's book author who has 
written 200+ personalised storybooks for kids aged 3-8.
You write simple, joyful stories where the child is always 
the hero. Your language is age-appropriate and rhythmic.

CONTEXT:
You are writing a personalised storybook for a real child.
Child's name: {request.child_name}
Child's age: {request.age} years old
Their favourite thing: {request.favourite_thing}
Story theme: {request.theme}
This story will be printed as a physical book for the child.
The child WILL see their own name on every page.

TASK:
Write an 8-page children's storybook following these rules:
1. Each page has exactly 2-3 sentences
2. Use only simple words a {request.age}-year-old understands
3. Use {request.child_name}'s name on every page naturally
4. Include {request.favourite_thing} meaningfully in the plot
5. Story structure: setup → problem → solution → happy ending
6. Page 8 must end with a warm 1-line moral lesson

FORMAT:
Return ONLY this structure, nothing else before or after:

PAGE 1:
[2-3 sentences]

PAGE 2:
[2-3 sentences]

PAGE 3:
[2-3 sentences]

PAGE 4:
[2-3 sentences]

PAGE 5:
[2-3 sentences]

PAGE 6:
[2-3 sentences]

PAGE 7:
[2-3 sentences]

PAGE 8:
[2-3 sentences]

MORAL: [one warm sentence]
"""


# ── Call OpenAI GPT-4o-mini ─────────────────────────────
def generate_story(request: StoryRequest) -> str:

    # Initialise OpenAI client
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Build our 4-layer prompt
    prompt = build_story_prompt(request)

    # Call GPT-4o-mini — fast, cheap, great for creative writing
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a children's book author. Follow format instructions exactly."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=1024,
        temperature=0.8      # Slightly creative — good for stories
    )

    return response.choices[0].message.content


# ── Save story to output file ────────────────────────────
def save_story(story: str, child_name: str) -> str:
    os.makedirs("outputs", exist_ok=True)
    filename = f"outputs/story_{child_name.lower()}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(story)

    return filename


# ── Cost estimator — know what you're spending ──────────
def estimate_cost(story: str) -> str:
    tokens = len(story.split()) * 1.3   # rough token estimate
    cost_usd = (tokens / 1_000_000) * 0.60  # GPT-4o-mini output price
    cost_inr = cost_usd * 83
    return f"~₹{cost_inr:.4f} per story"


# ── Main runner ──────────────────────────────────────────
if __name__ == "__main__":

    # 🔧 Change these values to test different children
    test_request = StoryRequest(
        child_name="Arjun",
        age=5,
        theme="jungle adventure",
        favourite_thing="elephants"
    )

    print(f"✨ Generating story for {test_request.child_name}...")
    print(f"📖 Theme: {test_request.theme}")
    print("─" * 50)

    story = generate_story(test_request)
    filepath = save_story(story, test_request.child_name)
    cost = estimate_cost(story)

    print(story)
    print("─" * 50)
    print(f"✅ Saved to: {filepath}")
    print(f"💰 Estimated cost: {cost}")