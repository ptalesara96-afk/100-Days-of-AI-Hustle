import { z } from "zod"

// ── This mirrors your Pydantic model exactly ─────────
export const storySchema = z.object({
  child_name: z
    .string()
    .min(1, "Child's name is required")
    .max(50, "Name too long")
    .regex(/^[a-zA-Z\s]+$/, "Name must contain letters only"),

  age: z
    .number({
      message: "Age is required and must be a number",
    })
    .int("Age must be a whole number")
    .min(3, "Child must be at least 3 years old")
    .max(10, "Child must be 10 years or younger"),

  theme: z.enum([
    "jungle_adventure",
    "space_rescue",
    "underwater_treasure",
    "magical_garden",
    "superhero_day",
  ], {
    message: "Please select a story theme",
  }),

  favourite_thing: z
    .string()
    .min(2, "Please enter something your child loves")
    .max(50, "Too long — keep it simple"),
   hair_color:      z.enum([
        "black", "dark brown", "brown"
    ]).default("black"),
    hair_type:       z.enum([
        "straight", "curly", "wavy"
    ]).default("straight"),
    hair_length:     z.enum([
        "short", "medium", "long"
    ]).default("short"),
    skin_tone:       z.enum([
        "light", "wheatish", "medium brown",
        "brown", "dark brown"
    ]).default("wheatish"),
    face_shape:      z.enum([
        "round", "oval", "chubby"
    ]).default("round"),
    eye_color:       z.enum([
        "black", "dark brown", "brown"
    ]).default("brown"),
    eye_size:        z.enum([
        "small", "medium", "big"
    ]).default("medium"),
    special_feature: z.enum([
        "None", "dimple", "mole",
        "freckles", "birthmark"
    ]).default("None"),
    clothing_color:  z.string().default("blue"),
    clothing_style:  z.enum([
        "t-shirt", "dress", "kurta",
        "shorts", "jeans"
    ]).default("t-shirt"),  
})

// ── Type inferred from schema ─────────────────────────
export type StoryFormData = z.infer<typeof storySchema>

// ── Theme display labels ──────────────────────────────
export const themeLabels: Record<string, string> = {
  jungle_adventure:    "🌿 Jungle Adventure",
  space_rescue:        "🚀 Space Rescue",
  underwater_treasure: "🐠 Underwater Treasure",
  magical_garden:      "🌸 Magical Garden",
  superhero_day:       "⚡ Superhero Day",
}