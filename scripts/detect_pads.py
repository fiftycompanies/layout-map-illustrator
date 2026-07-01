#!/usr/bin/env python3
"""1단계: 원본 배치도에서 색으로 칸 검출 → centroid 좌표.

순수 PIL(numpy 불필요) BFS 연결요소. 색 임계값은 소스에 맞게 보정할 것.
사용: python detect_pads.py <layout.png> [--color red|purple|yellow|green|pink|blue]
      python detect_pads.py <layout.png> --sample X Y     # 특정 픽셀 색 샘플(임계값 보정용)

출력: 색별 centroid 리스트(원본 픽셀좌표). 이걸 사용자 번호규칙대로 coord_map.json에 배정.
"""
import sys, json
from collections import deque
from PIL import Image

# 기본 색 임계값 (소스마다 다름 → --sample로 실측 후 조정)
MASKS = {
    "red":    lambda r, g, b: r > 190 and g < 145 and b < 135 and (r-g) > 50 and (r-b) > 55,
    "purple": lambda r, g, b: 105 < r < 205 and 90 < g < 170 and b > 145 and (b-g) > 25 and (b-r) > 8,
    "yellow": lambda r, g, b: r > 210 and g > 190 and b < 165 and (r-b) > 75 and abs(r-g) < 50,
    "green":  lambda r, g, b: 110 < r < 210 and g > 180 and 100 < b < 195 and (g-r) > 25 and (g-b) > 25,
    "pink":   lambda r, g, b: r > 200 and 70 < g < 190 and b > 150 and (r-g) > 55 and b > g - 10,
    "blue":   lambda r, g, b: 90 < r < 185 and 150 < g < 215 and b > 195 and (b-r) > 45,
}


def comps(px, W, H, fn, box=None, min_area=35, min_wh=6):
    x0, y0, x1, y1 = box or (0, 0, W, H)
    s = set()
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y][:3]
            if fn(r, g, b):
                s.add((x, y))
    out = []
    while s:
        seed = s.pop(); q = deque([seed]); pts = [seed]
        while q:
            x, y = q.popleft()
            for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                if (nx, ny) in s:
                    s.discard((nx, ny)); q.append((nx, ny)); pts.append((nx, ny))
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        if len(pts) >= min_area and max(xs)-min(xs) >= min_wh and max(ys)-min(ys) >= min_wh:
            out.append((sum(xs)//len(xs), sum(ys)//len(ys)))
    return out


def main():
    path = sys.argv[1]
    im = Image.open(path).convert("RGB"); W, H = im.size; px = im.load()
    if "--sample" in sys.argv:
        i = sys.argv.index("--sample"); x, y = int(sys.argv[i+1]), int(sys.argv[i+2])
        print(f"pixel ({x},{y}) = {px[x, y]}"); return
    colors = [sys.argv[sys.argv.index("--color")+1]] if "--color" in sys.argv else list(MASKS)
    result = {}
    for c in colors:
        pts = comps(px, W, H, MASKS[c])
        result[c] = pts
        print(f"{c}: {len(pts)}")
        for p in sorted(pts, key=lambda t: (t[1], t[0])):
            print("   ", p)
    json.dump(result, open("detected_pads.json", "w"))
    print("\n→ detected_pads.json 저장. 사용자 번호규칙대로 coord_map.json 에 배정하세요.")


if __name__ == "__main__":
    main()
