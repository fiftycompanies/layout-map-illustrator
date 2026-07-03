"""Split a vtracer SVG into semantic layer files by fill color.

Usage:
  python split_by_color.py terrain.svg --group land="#FCDFC5" \
      --group water="#B2D9FB,#AFD4F7" --group roads="#ECAB78,#EB9C61,#E4A778" \
      [--rest detail.svg]

Each --group name="#hex,#hex..." writes <name>.svg containing the matching paths
(stacking order preserved). Unmatched paths go to the --rest file (default rest.svg).
"""
import argparse, re

ap = argparse.ArgumentParser()
ap.add_argument("svg")
ap.add_argument("--group", action="append", default=[], metavar='name="#hex,#hex"')
ap.add_argument("--rest", default="rest.svg")
args = ap.parse_args()

src = open(args.svg).read()
head = re.search(r"<svg[^>]*>", src).group(0)
paths = re.findall(r"<path[^>]*/>", src)

def fill_of(p):
    m = re.search(r'fill="([^"]+)"', p)
    return (m.group(1) if m else "").lower()

taken = set()
for g in args.group:
    name, colors = g.split("=", 1)
    colorset = {c.strip().lower() for c in colors.strip('"').split(",")}
    idxs = [i for i, p in enumerate(paths) if fill_of(p) in colorset and i not in taken]
    taken.update(idxs)
    open(f"{name}.svg", "w").write(head + "".join(paths[i] for i in idxs) + "</svg>")
    print(f"{name}.svg: {len(idxs)} paths")

rest = [p for i, p in enumerate(paths) if i not in taken]
open(args.rest, "w").write(head + "".join(rest) + "</svg>")
print(f"{args.rest}: {len(rest)} paths")
