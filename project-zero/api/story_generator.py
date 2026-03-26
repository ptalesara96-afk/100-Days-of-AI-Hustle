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


def build_story_prompt(request: StoryRequest) -> str:
    return f"""
ROLE:
You are a warm, imaginative children's book author with
200+ published personalised storybooks for kids aged 3-8.
You write simple, joyful stories where the child is always
the hero. Your language is rhythmic and age-appropriate.

CONTEXT:
Child's name: {request.child_name}
Child's age: {request.age} years old
Favourite thing: {request.favourite_thing}
Story theme: {request.theme}
This will be printed as a real book the child will keep.

CHAIN OF THOUGHT — Think through this first:
Before writing, briefly plan:
- What is {request.child_name}'s goal in this story?
- What obstacle will they face?
- How does {request.favourite_thing} help solve it?
- What is the warm lesson at the end?
Write your plan in 2 lines, then write the story.

FEW-SHOT EXAMPLE — Match this quality exactly:
(Example for a different child — do NOT copy this)

PAGE 1:
Mia loved butterflies more than anything in the world.
She could name every colour and every wing shape by heart.
One morning, she found a tiny butterfly stuck in the rain.

PAGE 2:
"Don't worry," said Mia softly, "I'll help you fly again."
She made a little shelter from a big green leaf.
The butterfly looked up at her with tiny grateful eyes.

(End of example — now write {request.child_name}'s story)

TASK:
Write an 8-page story following these rules exactly:
1. Each page: exactly 3 sentences. No more, no less.
2. Words a {request.age}-year-old understands only.
3. Use {request.child_name} by name on EVERY page.
4. {request.favourite_thing} must appear in the plot
   and help solve the main problem.
5. Structure: Page 1-2 setup → Page 3-4 problem →
   Page 5-6 challenge → Page 7 solution → Page 8 ending

FORMAT:
Return ONLY this — no preamble, no plan in output,
no extra text before PAGE 1 or after MORAL:

PAGE 1:
[3 sentences]

PAGE 2:
[3 sentences]

PAGE 3:
[3 sentences]

PAGE 4:
[3 sentences]

PAGE 5:
[3 sentences]

PAGE 6:
[3 sentences]

PAGE 7:
[3 sentences]

PAGE 8:
[3 sentences]

MORAL: [One warm sentence beginning with "Remember:"]
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