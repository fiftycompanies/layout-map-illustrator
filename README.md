# Layout Map Illustrator

Turn a plain facility **layout map** (campground, parking lot, resort, venue…) into a
pretty **hand-drawn / watercolor / cartoon** illustrated map — while keeping every
site number and label **100% accurate**.

Built as a [Claude Code](https://docs.claude.com/en/docs/claude-code) skill, but the
scripts are plain Python and run standalone.

## Why this exists

Image models (Nano Banana Pro, Stable Diffusion + ControlNet, etc.) make beautiful
illustrated maps — but they **always garble the small text and numbers** inside the
image, no matter how careful the prompt. For a site map, wrong numbers are useless.

The trick that actually works:

> **Art by AI, text by code.**
> 1. Build an *accurate base* with blank colored pads at the exact positions.
> 2. Let the AI **restyle** it (positions preserved, all text removed).
> 3. **Stamp the labels with code** on top — pixel-perfect, never garbled.

## Pipeline

| Step | Script | Does |
|------|--------|------|
| 1 | `scripts/detect_pads.py` | Color-detect site boxes on the source → centroid coordinates |
| 2 | `scripts/build_base.py` | Erase deletions + redraw blank solid pads → `base_blank.png` (position anchor) |
| 3 | `scripts/restyle.py` | Nano Banana Pro restyles the base to watercolor/cartoon (keeps positions, drops text) |
| 4 | `scripts/overlay_labels.py` | Stamp every number/name with a font + white halo at the exact coords |

## v2 — Layered editable map (Figma-ready)

v1 gives you a pretty flat PNG. **v2 gives you an SVG where every element is its own
editable layer** — drag it into Figma and reshape the land outline, widen the river,
move individual trees, edit every number as native text. Watercolor texture is applied
as a clip mask, so **reshaping the outline re-flows the texture automatically**.

| Step | Script | Does |
|------|--------|------|
| 1 | [`vtracer`](https://github.com/visioncortex/vtracer) | Vectorize the source terrain (stacked SVG) |
| 2 | `scripts/split_by_color.py` | Split stacked paths into semantic layers (water / roads / boundary / detail) |
| 3 | `scripts/land_shape.py` | Boolean-subtract paper from the base → **one editable land polygon** (svgpathtools + shapely) |
| 4 | `scripts/gen_textures.py` | Generate seamless watercolor washes + a tree/bush/building sticker sheet |
| 5 | `scripts/cut_sprites.py` | Cut the sticker sheet into individual transparent PNGs |
| 6 | (compose per map) | Assemble one layered SVG: shapes + clip-mask textures + sticker assets + pads + text labels + a copy-paste asset palette |

See [`SKILL.md`](SKILL.md) for the full workflow and the gotchas we learned the hard way.

## Install (as a Claude Code skill)

```bash
git clone https://github.com/fiftycompanies/layout-map-illustrator.git
cp -R layout-map-illustrator ~/.claude/skills/layout-map-illustrator
```

Then just say: *"redraw this campground map, keep the numbers accurate"* and attach the layout image.

## Use standalone

```bash
export GOOGLE_API_KEY=...          # for the restyle step
pip install google-genai pillow

# 1) detect pads (tune color thresholds with --sample X Y)
python scripts/detect_pads.py layout.png
# → hand-assign numbers to centroids → coord_map.json  (see examples/coord_map.example.json)

# 2) blank accurate base
python scripts/build_base.py layout.png coord_map.json

# 3) restyle (watercolor | cartoon)
python scripts/restyle.py base_blank.png --tone cartoon

# 4) stamp labels
python scripts/overlay_labels.py tone_cartoon_1.png coord_map.json
```

## Notes

- Image generation uses Google's Gemini image model (`gemini-3-pro-image-preview`). Swap in
  any restyle backend that preserves composition (e.g. ControlNet lineart) — step 4 still applies.
- `overlay_labels.py` defaults to a macOS Korean font; set `FONT` to any font with the glyphs you need.
- Color thresholds in `detect_pads.py` are starting points — calibrate per source with `--sample`.

## License

[MIT](LICENSE) © 2026 fiftycompanies. Free for any company to use, modify, and ship.
