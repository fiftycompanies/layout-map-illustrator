#!/usr/bin/env python3
"""2단계: 빈칸 정확본(clean base) 생성.

coord_map.json(원본좌표 + 번호배정)과 삭제영역을 받아:
 - 삭제 대상(매점·오솔길 등)을 배경색으로 덮고
 - 모든 칸을 번호 없는 solid 색 rounded box 로 재도색(원본 작은 라벨 덮음)
 → base_blank.png (원본*S 캔버스). 이게 "위치 앵커".

coord_map.json 형식:
{
 "neuti": {"1":[x,y], ...}, "jajak":{...}, "A":{...}, "B":{...}, "C":{...}, "D":{...},
 "macha": [[x,y],[x,y]],
 "erase": [[x0,y0,x1,y1], ...]   # 삭제 사각형(원본좌표). 매점·오솔길 등.
}
사용: python build_base.py <layout.png> <coord_map.json> [--scale 2]
"""
import sys, json
from PIL import Image, ImageDraw

TAN = (250, 224, 195)  # 배경색(소스에 맞게 조정)
COL = {"neuti": (222, 108, 94), "jajak": (168, 122, 196), "A": (242, 214, 86),
       "B": (150, 206, 120), "C": (236, 120, 182), "D": (120, 176, 226), "macha": (176, 120, 70)}


def main():
    layout, cmap = sys.argv[1], sys.argv[2]
    S = int(sys.argv[sys.argv.index("--scale")+1]) if "--scale" in sys.argv else 2
    C = json.load(open(cmap))
    im = Image.open(layout).convert("RGB"); W, H = im.size
    d0 = ImageDraw.Draw(im)
    for box in C.get("erase", []):
        d0.rectangle(box, fill=TAN)
    im = im.resize((W*S, H*S), Image.LANCZOS)
    d = ImageDraw.Draw(im)

    def pad(cx, cy, fill, hw=16, hh=12):
        x, y = cx*S, cy*S
        d.rounded_rectangle([x-hw, y-hh, x+hw, y+hh], radius=5, fill=fill, outline=(70, 55, 60), width=2)

    for grp in ("neuti", "jajak", "A", "B", "C", "D"):
        for _, (x, y) in C.get(grp, {}).items():
            pad(x, y, COL[grp])
    for (x, y) in C.get("macha", []):
        pad(x, y, COL["macha"])
    im.save("base_blank.png")
    print("saved base_blank.png", im.size)


if __name__ == "__main__":
    main()
