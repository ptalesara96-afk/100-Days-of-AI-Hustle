import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv
from api.character import CharacterProfile
from api.image_generator import generate_all_images
from fastapi.staticfiles import StaticFiles

# Load env BEFORE app init — critical order
load_dotenv()

# Import our story generator
from api.story_generator import StoryRequest, generate_story, save_story

# ── FastAPI app setup ────────────────────────────────
app = FastAPI(
    title="Project Zero — Story Generator API",
    description="Personalised children's storybook generator",
    version="1.0.0"
)

# ── CORS — allows your Next.js frontend to call this ─
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://192.168.1.122:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

# ── Request schema with Pydantic validation ──────────
# ── Updated Request — now includes character fields ──
class StoryRequestBody(BaseModel):
    # Story fields
    child_name:      str = Field(..., min_length=1, max_length=50)
    age:             int = Field(..., ge=3, le=10)
    theme:           str = Field(..., min_length=3, max_length=100)
    favourite_thing: str = Field(..., min_length=2, max_length=50)

    # Character description fields — all optional with defaults
    hair_color:       str = Field(default="black")
    hair_type:        str = Field(default="straight")
    hair_length:      str = Field(default="short")
    skin_tone:        str = Field(default="wheatish")
    face_shape:       str = Field(default="round")
    eye_color:        str = Field(default="brown")
    eye_size:         str = Field(default="medium")
    special_feature:  str = Field(default="None")
    clothing_color:   str = Field(default="blue")
    clothing_style:   str = Field(default="t-shirt")

    @validator('child_name')
    def name_must_be_clean(cls, v):
        if not v.replace(' ', '').isalpha():
            raise ValueError('Name must contain letters only')
        return v.strip().title()


# ── Updated Response — now includes image URLs ────────
class StoryResponse(BaseModel):
    child_name:              str
    theme:                   str
    story_text:              str
    pages:                   list[str]
    moral:                   str
    image_urls:              list[str]  # NEW
    cost_inr:                float
    generation_time_seconds: float

# ── Parse raw story text into pages list ─────────────
def parse_story_into_pages(story_text: str) -> tuple[list, str]:
    pages = []
    moral = ""
    current_page = []

    for line in story_text.strip().split('\n'):
        line = line.strip()
        if line.startswith('PAGE'):
            if current_page:
                pages.append(' '.join(current_page))
            current_page = []
        elif line.startswith('MORAL:'):
            moral = line.replace('MORAL:', '').strip()
        elif line:
            current_page.append(line)

    if current_page:
        pages.append(' '.join(current_page))

    return pages, moral


# ── Health check endpoint ────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "story-generator"}


# ── Main story generation endpoint ──────────────────
@app.post("/generate-story", response_model=StoryResponse)
async def create_story(request: StoryRequestBody):
    try:
        start_time = time.time()

        # ── Step 1: Build story request ───────────────
        story_request = StoryRequest(
            child_name=request.child_name,
            age=request.age,
            theme=request.theme,
            favourite_thing=request.favourite_thing
        )

        # ── Step 2: Generate story text ───────────────
        print(f"📖 Generating story for "
              f"{request.child_name}...")
        story_text = generate_story(story_request)
        pages, moral = parse_story_into_pages(story_text)
        print(f"✅ Story done — {len(pages)} pages")

        # ── Step 3: Build character profile ──────────
        profile = CharacterProfile(
            child_name=request.child_name,
            age=request.age,
            hair_color=request.hair_color,
            hair_type=request.hair_type,
            hair_length=request.hair_length,
            skin_tone=request.skin_tone,
            face_shape=request.face_shape,
            eye_color=request.eye_color,
            eye_size=request.eye_size,
            special_feature=request.special_feature,
            clothing_color=request.clothing_color,
            clothing_style=request.clothing_style
        )

        # ── Step 4: Generate images ───────────────────
        print(f"🎨 Generating illustrations...")
        image_paths = generate_all_images(
            profile=profile,
            pages=pages,
            favourite_thing=request.favourite_thing
        )

        # ── Step 5: Build public URLs ─────────────────
        # Images served from /static/images/
        image_urls = [
            f"/static/{path.replace('static/', '')}"
            if path else ""
            for path in image_paths
        ]

        # ── Step 6: Calculate metrics ─────────────────
        generation_time = round(time.time() - start_time, 2)
        tokens_estimate = len(story_text.split()) * 1.3
        story_cost      = (tokens_estimate / 1_000_000) \
                          * 0.60 * 83
        image_cost      = len([p for p in image_paths if p]) \
                          * 0.04 * 83   # $0.04 per image
        total_cost_inr  = round(story_cost + image_cost, 2)

        # ── Step 7: Save story text ───────────────────
        save_story(story_text, request.child_name)

        return StoryResponse(
            child_name=request.child_name,
            theme=request.theme,
            story_text=story_text,
            pages=pages,
            moral=moral,
            image_urls=image_urls,
            cost_inr=total_cost_inr,
            generation_time_seconds=generation_time
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )
    try:
        start_time = time.time()

        # Build StoryRequest for generator
        story_request = StoryRequest(
            child_name=request.child_name,
            age=request.age,
            theme=request.theme,
            favourite_thing=request.favourite_thing
        )

        # Generate story via GPT-4o-mini
        story_text = generate_story(story_request)

        # Parse into structured pages
        pages, moral = parse_story_into_pages(story_text)

        # Calculate generation time + cost
        generation_time = round(time.time() - start_time, 2)
        tokens_estimate = len(story_text.split()) * 1.3
        cost_inr = round((tokens_estimate / 1_000_000) * 0.60 * 83, 4)

        # Save to file
        save_story(story_text, request.child_name)

        return StoryResponse(
            child_name=request.child_name,
            theme=request.theme,
            story_text=story_text,
            pages=pages,
            moral=moral,
            cost_inr=cost_inr,
            generation_time_seconds=generation_time
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Story generation failed: {str(e)}"
        )