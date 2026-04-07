"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { storySchema, StoryFormData, themeLabels } from "@/lib/schema"
import { generateStory, StoryResponse } from "@/lib/api"

// ── Loading states ────────────────────────────────────
type Status = "idle" | "loading" | "success" | "error"

export default function Home() {
  const [status, setStatus]   = useState<Status>("idle")
  const [story, setStory]     = useState<StoryResponse | null>(null)
  const [error, setError]     = useState<string>("")

  // ── React Hook Form setup ───────────────────────────
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<StoryFormData>({
    resolver: zodResolver(storySchema) as never,
    defaultValues: {
      hair_color: "black",
      hair_type: "straight",
      hair_length: "short",
      skin_tone: "wheatish",
      eye_color: "brown",
      special_feature: "None",
      clothing_color: "blue",
      clothing_style: "t-shirt",
    },
  })

  // ── Form submit handler ─────────────────────────────
  const onSubmit = async (
  data: StoryFormData,
  e?: React.BaseSyntheticEvent
) => {
  e?.preventDefault()
  try {
    setStatus("loading")
      setError("")
      const result = await generateStory(data)
      setStory(result)
      setStatus("success")
    } catch (err: any) {
      setStatus("error")
      setError(
        err?.response?.data?.detail ||
        "Something went wrong. Please try again."
      )
    }
  }

  // ── Reset to form ───────────────────────────────────
  const handleReset = () => {
    setStatus("idle")
    setStory(null)
    setError("")
    reset()
  }

  // ─────────────────────────────────────────────────────
  // LOADING STATE
  // ─────────────────────────────────────────────────────
  if (status === "loading") {
    return (
      <main className="min-h-screen flex items-center justify-center bg-amber-50">
        <div className="text-center space-y-4">
          <div className="text-6xl animate-bounce">📖</div>
          <h2 className="text-2xl font-bold text-amber-800">
            Writing your story...
          </h2>
          <p className="text-amber-600">
            Our AI author is crafting something magical.
            This takes about 10 seconds.
          </p>
          <div className="flex justify-center gap-1 mt-4">
            {[0,1,2].map(i => (
              <div
                key={i}
                className="w-2 h-2 bg-amber-400 rounded-full animate-bounce"
                style={{ animationDelay: `${i * 0.15}s` }}
              />
            ))}
          </div>
        </div>
      </main>
    )
  }

  // ─────────────────────────────────────────────────────
  // SUCCESS STATE — STORY DISPLAY
  // ─────────────────────────────────────────────────────
  if (status === "success" && story) {
    return (
      <main className="min-h-screen bg-amber-50 py-12 px-4">
        <div className="max-w-2xl mx-auto space-y-6">

          {/* Header */}
          <div className="text-center space-y-2">
            <div className="text-5xl">🎉</div>
            <h1 className="text-3xl font-bold text-amber-800">
              {story.child_name}&apos;s Story is Ready!
            </h1>
            <p className="text-amber-600 text-sm">
              Generated in {story.generation_time_seconds}s
              · Cost: ₹{story.cost_inr.toFixed(4)}
            </p>
          </div>

          {/* Story Pages */}
       {/* Story Pages — Now With Images */}
{story.pages.map((page, index) => (
    <div
        key={index}
        className="bg-white rounded-2xl overflow-hidden
          shadow-sm border border-amber-100"
    >
        {/* Page Image */}
        {story.image_urls[index] && (
            <div className="w-full aspect-square
              bg-amber-50 overflow-hidden">
                <img
                    src={`http://localhost:8000${story.image_urls[index]}`}
                    alt={`Story page ${index + 1}`}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                        // Hide broken images gracefully
                        (e.target as HTMLImageElement)
                            .style.display = 'none'
                    }}
                />
            </div>
        )}

        {/* Page Text */}
        <div className="p-6">
            <div className="flex items-center gap-3 mb-3">
                <span className="bg-amber-100
                  text-amber-700 text-xs font-bold
                  px-3 py-1 rounded-full">
                    PAGE {index + 1}
                </span>
            </div>
            <p className="text-gray-700 leading-relaxed
              text-lg">
                {page}
            </p>
        </div>
    </div>
))}

          {/* Moral */}
          {story.moral && (
            <div className="bg-amber-100 rounded-2xl p-6 border border-amber-200">
              <p className="text-amber-800 font-medium text-center italic text-lg">
                ✨ {story.moral}
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 justify-center pt-4">
            <button
              onClick={handleReset}
              className="bg-amber-500 hover:bg-amber-600 text-white font-semibold px-6 py-3 rounded-xl transition-colors"
            >
              Create Another Story
            </button>
          </div>

        </div>
      </main>
    )
  }

  // ─────────────────────────────────────────────────────
  // MAIN FORM STATE
  // ─────────────────────────────────────────────────────
  return (
    <main className="min-h-screen bg-amber-50 py-12 px-4">
      <div className="max-w-md mx-auto">

        {/* Header */}
        <div className="text-center mb-8 space-y-2">
          <div className="text-5xl">📚</div>
          <h1 className="text-3xl font-bold text-amber-800">
            Your Child&apos;s Story
          </h1>
          <p className="text-amber-600">
            A personalised AI storybook in seconds
          </p>
        </div>

        {/* Form */}
        <form
          onSubmit={handleSubmit(onSubmit)}
          method="post"
          action="#"
          className="bg-white rounded-2xl p-6 shadow-sm border border-amber-100 space-y-5"
        >

          {/* Child Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Child&apos;s Name *
            </label>
            <input
              {...register("child_name")}
              placeholder="e.g. Arjun"
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-gray-800 focus:outline-none focus:ring-2 focus:ring-amber-300 transition"
            />
            {errors.child_name && (
              <p className="text-red-500 text-xs mt-1">
                {errors.child_name.message}
              </p>
            )}
          </div>

          {/* Age */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Age *
            </label>
            <input
              {...register("age", { valueAsNumber: true })}
              type="number"
              placeholder="e.g. 5"
              min={3}
              max={10}
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-gray-800 focus:outline-none focus:ring-2 focus:ring-amber-300 transition"
            />
            {errors.age && (
              <p className="text-red-500 text-xs mt-1">
                {errors.age.message}
              </p>
            )}
          </div>

          {/* Favourite Thing */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Favourite Thing *
            </label>
            <input
              {...register("favourite_thing")}
              placeholder="e.g. elephants, rockets, dinosaurs"
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-gray-800 focus:outline-none focus:ring-2 focus:ring-amber-300 transition"
            />
            {errors.favourite_thing && (
              <p className="text-red-500 text-xs mt-1">
                {errors.favourite_thing.message}
              </p>
            )}
          </div>
          {/* Divider */}
<div className="border-t border-amber-100 pt-4">
    <p className="text-xs font-semibold text-amber-600
      uppercase tracking-wide mb-4">
        Describe Your Child
    </p>

    {/* Hair */}
    <div className="grid grid-cols-3 gap-2 mb-3">
        <div>
            <label className="block text-xs text-gray-500 mb-1">
                Hair Color
            </label>
            <select {...register("hair_color")}
                className="w-full border border-gray-200
                  rounded-lg px-2 py-2 text-sm
                  focus:outline-none focus:ring-2
                  focus:ring-amber-300 bg-white">
                <option value="black">Black</option>
                <option value="dark brown">Dark Brown</option>
                <option value="brown">Brown</option>
            </select>
        </div>
        <div>
            <label className="block text-xs text-gray-500 mb-1">
                Hair Type
            </label>
            <select {...register("hair_type")}
                className="w-full border border-gray-200
                  rounded-lg px-2 py-2 text-sm
                  focus:outline-none focus:ring-2
                  focus:ring-amber-300 bg-white">
                <option value="straight">Straight</option>
                <option value="curly">Curly</option>
                <option value="wavy">Wavy</option>
            </select>
        </div>
        <div>
            <label className="block text-xs text-gray-500 mb-1">
                Hair Length
            </label>
            <select {...register("hair_length")}
                className="w-full border border-gray-200
                  rounded-lg px-2 py-2 text-sm
                  focus:outline-none focus:ring-2
                  focus:ring-amber-300 bg-white">
                <option value="short">Short</option>
                <option value="medium">Medium</option>
                <option value="long">Long</option>
            </select>
        </div>
    </div>

    {/* Face + Eyes */}
    <div className="grid grid-cols-3 gap-2 mb-3">
        <div>
            <label className="block text-xs text-gray-500 mb-1">
                Skin Tone
            </label>
            <select {...register("skin_tone")}
                className="w-full border border-gray-200
                  rounded-lg px-2 py-2 text-sm
                  focus:outline-none focus:ring-2
                  focus:ring-amber-300 bg-white">
                <option value="light">Light</option>
                <option value="wheatish">Wheatish</option>
                <option value="medium brown">Medium</option>
                <option value="brown">Brown</option>
                <option value="dark brown">Dark</option>
            </select>
        </div>
        <div>
            <label className="block text-xs text-gray-500 mb-1">
                Eye Color
            </label>
            <select {...register("eye_color")}
                className="w-full border border-gray-200
                  rounded-lg px-2 py-2 text-sm
                  focus:outline-none focus:ring-2
                  focus:ring-amber-300 bg-white">
                <option value="black">Black</option>
                <option value="dark brown">Dark Brown</option>
                <option value="brown">Brown</option>
            </select>
        </div>
        <div>
            <label className="block text-xs text-gray-500 mb-1">
                Special Feature
            </label>
            <select {...register("special_feature")}
                className="w-full border border-gray-200
                  rounded-lg px-2 py-2 text-sm
                  focus:outline-none focus:ring-2
                  focus:ring-amber-300 bg-white">
                <option value="None">None</option>
                <option value="dimple">Dimple</option>
                <option value="mole">Mole</option>
                <option value="freckles">Freckles</option>
            </select>
        </div>
    </div>

    {/* Clothing */}
    <div className="grid grid-cols-2 gap-2">
        <div>
            <label className="block text-xs text-gray-500 mb-1">
                Favourite Color
            </label>
            <input
                {...register("clothing_color")}
                placeholder="e.g. red, blue, yellow"
                className="w-full border border-gray-200
                  rounded-lg px-3 py-2 text-sm
                  focus:outline-none focus:ring-2
                  focus:ring-amber-300"
            />
        </div>
        <div>
            <label className="block text-xs text-gray-500 mb-1">
                Clothing Style
            </label>
            <select {...register("clothing_style")}
                className="w-full border border-gray-200
                  rounded-lg px-2 py-2 text-sm
                  focus:outline-none focus:ring-2
                  focus:ring-amber-300 bg-white">
                <option value="t-shirt">T-Shirt</option>
                <option value="dress">Dress</option>
                <option value="kurta">Kurta</option>
                <option value="shorts">Shorts</option>
            </select>
        </div>
    </div>
</div>

          {/* Story Theme */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Story Theme *
            </label>
            <select
              {...register("theme")}
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-gray-800 focus:outline-none focus:ring-2 focus:ring-amber-300 transition bg-white"
            >
              <option value="">Select a theme...</option>
              {Object.entries(themeLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
            {errors.theme && (
              <p className="text-red-500 text-xs mt-1">
                {errors.theme.message}
              </p>
            )}
          </div>

          {/* Error Message */}
          {status === "error" && (
            <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-3">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            className="w-full bg-amber-500 hover:bg-amber-600 text-white font-bold py-4 rounded-xl transition-colors text-lg"
          >
            ✨ Create My Story
          </button>

        </form>

        {/* Footer note */}
        <p className="text-center text-amber-500 text-xs mt-4">
          Story generates in ~10 seconds · Free preview
        </p>

      </div>
    </main>
  )
}
