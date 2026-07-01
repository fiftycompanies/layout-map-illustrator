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
