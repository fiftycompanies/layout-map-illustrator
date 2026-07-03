"""Generate seamless watercolor wash textures + a sticker sheet of map assets
(trees, bushes, buildings) with Nano Banana Pro (Gemini image model).

Usage:
  export GOOGLE_API_KEY=...
  pip install google-genai
  python gen_textures.py --tone watercolor    # textures + sticker sheet for a tone
  python gen_textures.py --tone realistic --only sprite_sheet
"""
import argparse, os, sys
from google import genai
from google.genai import types

JOBS = {
    "watercolor": {
        "tex_land.png": "Seamless watercolor wash texture in warm light tan cream color, soft paper grain, subtle organic blotches, uniform coverage, no objects, no text, flat texture only, square",
        "tex_water.png": "Seamless watercolor wash texture in soft light blue, gentle water-like strokes, uniform coverage, no objects, no text, flat texture only, square",
        "tex_road.png": "Seamless watercolor wash texture in warm soft orange, subtle brush strokes, uniform coverage, no objects, no text, flat texture only, square",
        "sprite_sheet.png": "Sticker sheet: 8 separate cute hand-drawn watercolor illustration elements for a facility map, arranged in a grid with wide white gaps between them, on PURE WHITE background: 3 different green pine trees, 2 different round deciduous trees, 2 small green bushes, 1 small one-story building. Storybook watercolor style, no text, no numbers, each element fully separated from others",
    },
    # cartoon tone needs NO textures — use flat fills in the composer
    # (land orange ~#F2A75F, water teal ~#25C1C0, road ~#DE8A3F) and this sheet:
    "cartoon": {
        "sprite_sheet.png": "Sticker sheet: 8 separate flat vector cartoon map elements, arranged in a grid with wide white gaps between them, on PURE WHITE background: 2 stylized green pine trees with dark outline, 2 round deciduous trees with small brown trunk and dark outline, 1 green bush, 1 small teal one-story cabin with dark outline, 1 old-west covered wagon side view with dark outline, 1 compass rose. Clean flat colors, bold dark outlines, cute mobile game map style, no text, no numbers, each element fully separated",
    },
    "realistic": {
        "tex_land.png": "Seamless aerial photograph texture of short mowed green grass with subtle dirt patches, campground ground seen from directly above, uniform coverage, no objects, no text, square",
        "tex_water.png": "Seamless aerial photograph texture of clear river water with gentle ripples, teal-blue green, seen from directly above, uniform, no objects, no text, square",
        "tex_road.png": "Seamless aerial photograph texture of light brown dirt and fine gravel path, seen from directly above, uniform coverage, no objects, no text, square",
        "sprite_sheet.png": "Sticker sheet: 8 separate photorealistic miniature landscape elements seen from a high angle like a premium resort map illustration, arranged in a grid with wide white gaps between them, on PURE WHITE background: 3 pine trees, 2 leafy green deciduous trees, 2 low bushes, 1 small wooden cabin with brown roof. Realistic rendering, soft shadow directly under each object only, no text, no numbers, fully separated",
    },
}

ap = argparse.ArgumentParser()
ap.add_argument("--tone", default="watercolor", choices=list(JOBS))
ap.add_argument("--only", help="basename without .png (e.g. tex_land, sprite_sheet)")
args = ap.parse_args()

key = os.environ.get("GOOGLE_API_KEY") or sys.exit("set GOOGLE_API_KEY")
client = genai.Client(api_key=key)
tone_jobs = JOBS[args.tone]
jobs = {f"{args.only}.png": tone_jobs[f"{args.only}.png"]} if args.only else tone_jobs

for fname, prompt in jobs.items():
    res = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[prompt],
        config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
    )
    for part in res.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            open(fname, "wb").write(part.inline_data.data)
            print("saved", fname)
            break
    else:
        print("FAILED", fname)
