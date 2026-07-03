"""Cut a white-background sticker sheet into individual transparent PNGs.

Usage:
  python cut_sprites.py sprite_trees.png [-o sprites/] [--threshold 245] [--min-size 400]

Finds connected non-white components, merges overlapping boxes, crops each with
a small margin and turns near-white pixels transparent.
"""
import argparse, os
from collections import deque
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("sheet")
ap.add_argument("-o", "--outdir", default="sprites")
ap.add_argument("--threshold", type=int, default=245)
ap.add_argument("--min-size", type=int, default=400, help="min sampled pixels per component")
args = ap.parse_args()

im = Image.open(args.sheet).convert("RGB")
W, H = im.size
px = im.load()
TH = args.threshold

def is_obj(x, y):
    r, g, b = px[x, y]
    return not (r > TH and g > TH and b > TH)

visited = [[False] * W for _ in range(H)]
comps = []
for y0 in range(0, H, 4):
    for x0 in range(0, W, 4):
        if is_obj(x0, y0) and not visited[y0][x0]:
            q = deque([(x0, y0)]); visited[y0][x0] = True
            minx = maxx = x0; miny = maxy = y0; cnt = 0
            while q:
                x, y = q.popleft(); cnt += 1
                minx, miny = min(minx, x), min(miny, y)
                maxx, maxy = max(maxx, x), max(maxy, y)
                for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and not visited[ny][nx] and is_obj(nx, ny):
                        visited[ny][nx] = True; q.append((nx, ny))
            if cnt > args.min_size:
                comps.append((minx, miny, maxx, maxy))

def merge(boxes):
    out = []
    for b in sorted(boxes):
        for i, o in enumerate(out):
            if not (b[2] < o[0] - 10 or b[0] > o[2] + 10 or b[3] < o[1] - 10 or b[1] > o[3] + 10):
                out[i] = (min(o[0], b[0]), min(o[1], b[1]), max(o[2], b[2]), max(o[3], b[3])); break
        else:
            out.append(b)
    return out

prev = -1
while len(comps) != prev:
    prev = len(comps); comps = merge(comps)

comps.sort(key=lambda c: (c[1] // 300, c[0]))
rgba = Image.open(args.sheet).convert("RGBA")
os.makedirs(args.outdir, exist_ok=True)
for i, (x0, y0, x1, y1) in enumerate(comps):
    crop = rgba.crop((max(0, x0 - 6), max(0, y0 - 6), min(W, x1 + 6), min(H, y1 + 6)))
    d = crop.load()
    for yy in range(crop.height):
        for xx in range(crop.width):
            r, g, b, a = d[xx, yy]
            if r > TH and g > TH and b > TH:
                d[xx, yy] = (r, g, b, 0)
    crop.save(f"{args.outdir}/elem_{i}.png")
    print(f"elem_{i}.png", crop.size)
print("done:", len(comps))
