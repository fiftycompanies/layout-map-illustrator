---
name: layout-map-illustrator
description: Turn an existing facility layout map (campground, parking lot, resort, venue) into a pretty hand-drawn / watercolor / cartoon illustrated map — while keeping every site number and label 100% accurate. Trigger on requests like "redraw this site map", "make this layout map hand-drawn", "illustrate this campground map", or when given a layout image plus edit requests (renumbering, deletions, additions).
---

# Layout Map Illustrator

## Core principle (validated empirically)

> **"Art by AI, text by code."** Image models (Nano Banana Pro, ControlNet, etc.) **always garble small text/numbers** inside a generated picture — no matter how detailed the prompt. So **never let the AI render the labels. Draw the numbers/names with code on top.**

Validated pitfalls:
- ❌ Generating a **background only (pads removed)** → the AI re-composes the terrain (borders/roads shift) → your original coordinates no longer align.
- ✅ Restyling an **"accurate base" that keeps blank colored pads** → positions are preserved → labels stamped at the same coords line up.
- ❌ Color-detecting pads **on the watercolor output** → soft washes bleed the 6 zone colors together → detection fails.
- ✅ Always run color detection on the **crisp source / accurate base**, never the watercolor.
- ❌ Eyeballing pixel coordinates → unreliable. ✅ Use **color-detection centroids only.**

## 4-step pipeline

**0. Prep** — get the source layout image. Parse edit requests: renumbering (e.g. "office-left → tree1..13"), deletions (store, trail...), additions (wagons, parking...). Zoom (crop + LANCZOS) to read any hand-annotated numbering.

**1. Coordinate map — `scripts/detect_pads.py`**
Color-detect the pads on the source (pure-PIL BFS, no numpy). Tune thresholds via `--sample X Y`. Cross-check counts vs. expected. Assign numbers to centroids per the requested scheme → `coord_map.json` (source pixel coords). Include facility positions too.

**2. Blank accurate base — `scripts/build_base.py`**
Paint deletion areas over with the ground color; redraw every pad as a **blank solid colored rounded box** (covers the source's tiny labels) → `base_blank.png`. This is the position anchor — never remove pads (or the AI re-composes).

**3. Restyle to your tone — `scripts/restyle.py`**
Feed `base_blank` to Nano Banana Pro with *"restyle only, keep positions/size/composition, remove all text"*. Tone = `watercolor` or `cartoon` (swap the prompt). Output keeps the frame at a uniform scale factor.

**4. Stamp labels by code — `scripts/overlay_labels.py`**
Compute `f = output_width / base_width`. Label position = `source_coord × base_scale × f`. Stamp every label with a font + white halo. Numbers, zone codes, facility names, vertical parking label, legend.

**5. Verify (required)** — crop/zoom each region: labels on pads? deletions gone? no garbled text? Nudge overlay offset if a few px off, re-stamp.

## Run notes
- Image generation needs `GOOGLE_API_KEY` and `pip install google-genai`.
- Model: `gemini-3-pro-image-preview` (Nano Banana Pro), `response_modalities=["TEXT","IMAGE"]`.
- Fonts: set a font path with CJK/Latin coverage in `overlay_labels.py` (default is macOS `AppleSDGothicNeo.ttc`).

## Outputs
`base_blank.png` (anchor) · `tone_*.png` (restyled bg) · `map_FINAL_*_labeled.png` (final) · `coord_map.json`.

---

# v2 — Layered editable map (Figma-ready SVG)

The v1 pipeline outputs a flat PNG. v2 goes further: **every element — land shape,
water, roads, each tree, each pad, each label — is a separately editable layer.**
The user drags one SVG into Figma (or Canva) and can reshape the land outline,
widen the river, move trees, and edit numbers as native objects. Validated on a
real campground map (56 pads, 60+ labels, zero label corrections).

> **"Accuracy comes from code rendering, not AI generation."**
> A coordinate ledger (`coord_map.json`) is the single source of truth. Every
> derivative (flat guide map, hand-drawn tone, illustrated tone, editable SVG)
> is regenerated from the ledger, so edit requests never cause drift.

## v2 pipeline

**1. Coordinate ledger** — same as v1 step 1 (`detect_pads.py` centroids → `coord_map.json`).

**2. Vectorize the terrain** — [`vtracer`](https://github.com/visioncortex/vtracer)
(`filter_speckle=6, path_precision=1`) turns the source map into a stacked SVG
(~100-150 paths). Delete pad/label paths **at the vector level** (stacked output
means deleting a path just exposes the layer beneath — no holes). Never erase
pixels instead (stains and rings); never do subpath surgery (damages textures).

**3. Semantic layer split — `scripts/split_by_color.py`**
Group the stacked paths by fill color into layer files: land base, water, roads,
paved road, boundary dash — everything unmatched goes into one `detail` layer.

**4. True land shape — `scripts/land_shape.py`**
vtracer's stacking means "land" = base rectangle *visually carved* by paper-white
paths on top. Boolean-subtract them (svgpathtools samples the béziers → shapely
`difference` → `simplify(0.6)`) to get **one editable polygon** the user can
reshape point-by-point. `pip install svgpathtools shapely`.

**5. Watercolor textures + asset stickers — `scripts/gen_textures.py` + `scripts/cut_sprites.py`**
Generate 3 seamless watercolor washes (land/water/road) and one **sticker sheet**
(pines, deciduous trees, bushes, a small building — "wide white gaps, PURE WHITE
background"). Cut the sheet into individual transparent PNGs (connected components
+ white→alpha).

**6. Assemble the layered SVG** (compose per map — see structure below)
- Shapes get their texture via **`clipPath` masking**: `<clipPath id="clipLand"><path …/></clipPath>`
  `<image href="data:image/png;base64,…" clip-path="url(#clipLand)"/>` — so when the
  user reshapes the outline in Figma, **the texture follows the new shape**.
- Pads = `<rect rx>` (+ `transform="rotate(deg cx cy)"`), labels = `<text>` (imports as editable text).
- Add an **asset palette** group beside the canvas (one of each sticker, labeled) so
  users copy-paste more trees.
- Layer order: paper → land → water → roads → paved → boundary → detail → trees → pads → labels → palette.

**7. Deliver & verify** — screenshot the SVG headless (`chrome --headless --screenshot
--force-device-scale-factor=2`) and eyeball region crops. Then hand over the SVG:
**drag & drop into Figma** imports every group as native, editable layers.

## Figma editing guide (include it in your handoff)
- The clip-masked shapes import as `Clip path group` → texture `Rectangle` + `clip… > Vector` (the shape).
- Reshape: select the **Vector** in the Layers panel → press **Enter** (again if the
  first press only selects) → point-edit mode (a *Done* button appears on top).
- Multi-select points: **drag a marquee starting from empty space** (starting on a
  point drags that point) or Shift-click; drag any selected point to move them together.
- If a *Crop* panel shows up, the user grabbed the texture Rectangle, not the shape.

## v2 gotchas
- Figma MCP on a **Starter plan hits its tool-call limit within a few calls**
  (`use_figma`, screenshots included). The drag-&-drop SVG path is free and unlimited —
  prefer it for delivery; use the MCP only when you have quota.
- Canva import: serve the file from a URL that answers **HEAD** requests (Canva
  probes with HEAD before fetching — S3 presigned GET URLs fail with 403). A raw
  gist URL works; delete the gist after import.
- Text inside SVG imports into Figma as real text nodes; pick a font family that
  exists there (Figma will offer a substitute otherwise).
