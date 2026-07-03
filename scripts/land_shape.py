"""Boolean-subtract the paper/void paths from the base land rectangle
→ a single editable polygon path for the "land" layer.

Usage:
  pip install svgpathtools shapely
  python land_shape.py terrain.svg --base-fill "#FCDFC5" [--simplify 0.6] [-o land_shape.txt]

Input SVG: vtracer output (stacked paths). The path whose fill == --base-fill is
the base; every other path in the file is treated as a cutter (paper/void areas
that carve the land outline). Output: one or more `d` strings (one per line).
"""
import argparse, re
from svgpathtools import parse_path
from shapely.geometry import Polygon
from shapely.ops import unary_union

ap = argparse.ArgumentParser()
ap.add_argument("svg")
ap.add_argument("--base-fill", required=True)
ap.add_argument("--simplify", type=float, default=0.6)
ap.add_argument("--min-area", type=float, default=150)
ap.add_argument("-o", "--out", default="land_shape.txt")
ap.add_argument("--samples", type=int, default=900, help="points sampled per path")
args = ap.parse_args()

svg = open(args.svg).read()
raws = re.findall(r'<path d="([^"]+)" fill="([^"]+)"(?: transform="translate\(([-\d.]+),([-\d.]+)\)")?\s*/>', svg)

def to_poly(d, tx, ty):
    p = parse_path(d)
    pts = [(z.real + tx, z.imag + ty) for z in (p.point(i / args.samples) for i in range(args.samples + 1))]
    poly = Polygon(pts)
    return poly if poly.is_valid else poly.buffer(0)

base, holes = None, []
for d, fill, tx, ty in raws:
    poly = to_poly(d, float(tx or 0), float(ty or 0))
    if fill.lower() == args.base_fill.lower():
        base = poly
    else:
        holes.append(poly)
if base is None:
    raise SystemExit(f"no path with fill {args.base_fill}")

land = base.difference(unary_union(holes)).simplify(args.simplify)
geoms = sorted(land.geoms, key=lambda g: g.area, reverse=True) if land.geom_type == "MultiPolygon" else [land]
parts = []
for g in geoms:
    if g.area < args.min_area:
        continue
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in g.exterior.coords) + " Z"
    for ring in g.interiors:
        d += " M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in ring.coords) + " Z"
    parts.append(d)
open(args.out, "w").write("\n".join(parts))
print(f"{len(parts)} polygon(s) → {args.out}, main outline {len(list(geoms[0].exterior.coords))} pts")
