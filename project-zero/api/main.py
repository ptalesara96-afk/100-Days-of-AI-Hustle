import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

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
    allow_origins=["http://localhost:3000"],  # Next.js dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request schema with Pydantic validation ──────────
class StoryRequestBody(BaseModel):
    child_name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=3, le=10)  # age 3-10 only
    theme: str = Field(..., min_length=3, max_length=100)
    favourite_thing: str = Field(..., min_length=2, max_length=50)

    @validator('child_name')
    def name_must_be_clean(cls, v):
        if not v.replace(' ', '').isalpha():
            raise ValueError('Name must contain letters only')
        return v.strip().title()  # auto-capitalise


# ── Response schema ──────────────────────────────────
class StoryResponse(BaseModel):
    child_name: str
    theme: str
    story_text: str
    pages: list[str]
    moral: str
    cost_inr: float
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