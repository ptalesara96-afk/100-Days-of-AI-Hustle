import axios from "axios"
import { StoryFormData } from "./schema"

// ── API base URL from env ─────────────────────────────
const API_URL = process.env.NEXT_PUBLIC_API_URL

// ── Response type matching FastAPI response ───────────
export interface StoryResponse {
    child_name:              string
    theme:                   string
    story_text:              string
    pages:                   string[]
    moral:                   string
    image_urls:              string[]   // NEW
    cost_inr:                number
    generation_time_seconds: number
}
// ── Main API call ─────────────────────────────────────
export async function generateStory(
  data: StoryFormData
): Promise<StoryResponse> {
  const response = await axios.post<StoryResponse>(
    `${API_URL}/generate-story`,
    {
      child_name:      data.child_name,
      age:             data.age,
      theme:           data.theme.replace(/_/g, " "),
      favourite_thing: data.favourite_thing,
    },
    {
      timeout: 30000, // 30 seconds — AI can be slow
    }
  )
  return response.data
}