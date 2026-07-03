"""Generate seamless watercolor wash textures + a sticker sheet of map assets
(trees, bushes, buildings) with Nano Banana Pro (Gemini image model).

Usage:
  export GOOGLE_API_KEY=...
  pip install google-genai
  python gen_textures.py                      # default: land/water/road textures + tree sheet
  python gen_textures.py --only sprite_trees  # regenerate one output
"""
import argparse, os, sys
from google import genai
from google.genai import types

JOBS = {
    "tex_land.png": "Seamless watercolor wash texture in warm light tan cream color, soft paper grain, subtle organic blotches, uniform coverage, no objects, no text, flat texture only, square",
    "tex_water.png": "Seamless watercolor wash texture in soft light blue, gentle water-like strokes, uniform coverage, no objects, no text, flat texture only, square",
    "tex_road.png": "Seamless watercolor wash texture in warm soft orange, subtle brush strokes, uniform coverage, no objects, no text, flat texture only, square",
    "sprite_trees.png": "Sticker sheet: 8 separate cute hand-drawn watercolor illustration elements for a facility map, arranged in a grid with wide white gaps between them, on PURE WHITE background: 3 different green pine trees, 2 different round deciduous trees, 2 small green bushes, 1 small one-story building. Storybook watercolor style, no text, no numbers, each element fully separated from others",
}

ap = argparse.ArgumentParser()
ap.add_argument("--only", help="basename without .png (e.g. tex_land, sprite_trees)")
args = ap.parse_args()

key = os.environ.get("GOOGLE_API_KEY") or sys.exit("set GOOGLE_API_KEY")
client = genai.Client(api_key=key)
jobs = {f"{args.only}.png": JOBS[f"{args.only}.png"]} if args.only else JOBS

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
