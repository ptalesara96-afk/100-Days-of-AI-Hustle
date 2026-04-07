import os
import httpx
import base64
import asyncio
from pathlib import Path
from openai import OpenAI
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

from api.character import CharacterProfile, build_character_anchor, \
    build_image_prompt

load_dotenv()


# ── Scene descriptions — one per story page ──────────
SCENE_TEMPLATES = [
    "discovering something amazing for the first time, "
    "eyes wide with wonder and excitement",

    "meeting a new friend, both looking at each other "
    "with curiosity and joy",

    "facing a challenge, looking determined and brave",

    "trying hard to solve a problem, thinking carefully",

    "getting help from a friend, working together",

    "overcoming the challenge, pumping fist in victory",

    "celebrating success with friends, everyone cheering",

    "sitting peacefully at sunset, calm and happy, "
    "reflecting on the adventure"
]


def generate_scene_for_page(
    page_text: str,
    page_number: int,
    child_name: str,
    favourite_thing: str
) -> str:
    """
    Creates a scene description from the story page text.
    Incorporates the child's name and favourite thing.
    """
    # Use template as base — inject story context
    base_scene = SCENE_TEMPLATES[
        min(page_number - 1, len(SCENE_TEMPLATES) - 1)
    ]

    # Add favourite thing to scene naturally
    return (
        f"{base_scene}, "
        f"with {favourite_thing} nearby in the scene"
    )


def generate_single_image(
    client: OpenAI,
    prompt: str,
    page_number: int,
    child_name: str
) -> str | None:
    """
    Generates one image via OpenAI API.
    Saves to static/images/ folder.
    Returns the local file path.
    """
    try:
        response = client.images.generate(
            model="gpt-image-1",         # Use dall-e-3 on free tier
            prompt=prompt,            # Switch to gpt-image-1 on paid
            size="1024x1024",
            quality="standard",
            n=1,
            response_format="b64_json"
        )

        # Decode base64 image
        image_data = base64.b64decode(
            response.data[0].b64_json
        )

        # Process with Pillow — ensure consistent dimensions
        image = Image.open(BytesIO(image_data))
        image = image.resize(
            (1024, 1024),
            Image.Resampling.LANCZOS
        )

        # Save to static folder
        os.makedirs("static/images", exist_ok=True)
        filename = (
            f"static/images/"
            f"{child_name.lower()}_page{page_number}.png"
        )
        image.save(filename, "PNG", optimize=True)

        return filename

    except Exception as e:
        print(f"❌ Image generation failed page "
              f"{page_number}: {e}")
        return None


def generate_all_images(
    profile: CharacterProfile,
    pages: list[str],
    favourite_thing: str
) -> list[str]:
    """
    Generates all 8 story page images.
    Returns list of saved file paths.
    """
    client  = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    anchor  = build_character_anchor(profile)
    paths   = []

    print(f"🎨 Generating {len(pages)} illustrations...")
    print(f"   Character: {profile.child_name}")
    print(f"   Anchor: {anchor[:80]}...")

    for i, page_text in enumerate(pages, 1):
        print(f"   Page {i}/{len(pages)}...")

        # Build scene from page text
        scene = generate_scene_for_page(
            page_text, i,
            profile.child_name,
            favourite_thing
        )

        # Build full prompt with anchor
        prompt = build_image_prompt(anchor, scene, i)

        # Generate and save image
        path = generate_single_image(
            client, prompt, i, profile.child_name
        )

        if path:
            paths.append(path)
            print(f"   ✅ Page {i} saved: {path}")
        else:
            # Use placeholder if generation fails
            paths.append("")
            print(f"   ⚠️  Page {i} failed — placeholder used")

    print(f"✅ Generated {len([p for p in paths if p])} "
          f"/ {len(pages)} images")

    return paths