#!/usr/bin/env python3
"""4단계: 덧칠된 톤 배경 위에 라벨을 코드로 얹기 (크리스프, 뭉개짐 0).

정확본(base_blank, 원본*S)과 톤 배경은 같은 프레임 → 균일 배율 f = 톤폭/정확본폭.
라벨좌표 = 원본좌표 * S * f. 한글폰트 + 흰색 halo로 스탬프.

coord_map.json 에 fac(시설), macha 포함:
 "fac": {"사무실":[x,y], "화장실·샤워실·개수대":[x,y], "입구":[x,y], "도로":[x,y],
         "화악계곡":[x,y], "주차장":[x,y], "N":[x,y]}
사용: python overlay_labels.py tone_cartoon_1.png coord_map.json --base-scale 2
"""
import sys, json
from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
BASE_W = 1526.0  # 정확본 폭(원본 763 * 2). --base-scale 로 조정 가능
TXT = {"neuti": (95, 20, 20), "jajak": (45, 25, 95), "A": (95, 70, 10),
       "B": (20, 80, 30), "C": (125, 20, 85), "D": (20, 50, 125)}
PREFIX = {"neuti": "", "jajak": "", "A": "A", "B": "B", "C": "C", "D": "D"}


def main():
    tone_path, cmap = sys.argv[1], sys.argv[2]
    bs = int(sys.argv[sys.argv.index("--base-scale")+1]) if "--base-scale" in sys.argv else 2
    C = json.load(open(cmap))
    im = Image.open(tone_path).convert("RGB"); Ww, Hw = im.size
    base_w = float(C.get("_base_w", 763 * bs))
    f = Ww / base_w
    d = ImageDraw.Draw(im)
    Fnt = lambda s: ImageFont.truetype(FONT, s)

    def P(x, y):
        return (x * bs * f, y * bs * f)

    def lab(x, y, text, fs=15, col=(35, 25, 30), sw=3):
        px, py = P(x, y)
        d.text((px, py), text, font=Fnt(fs), fill=col, anchor="mm", stroke_width=sw, stroke_fill=(255, 255, 255))

    for grp in ("neuti", "jajak", "A", "B", "C", "D"):
        for n, (x, y) in C.get(grp, {}).items():
            fs = 16 if grp in ("neuti", "jajak") else 12
            lab(x, y, f"{PREFIX[grp]}{n}", fs, TXT[grp])
    # 마차방갈로 라벨(칸 아래)
    if C.get("macha"):
        mx = sum(p[0] for p in C["macha"]) // len(C["macha"])
        my = max(p[1] for p in C["macha"]) + 16
        lab(mx, my, "마차방갈로 1·2", 15, (30, 20, 20))
    # 시설
    for name, (x, y) in C.get("fac", {}).items():
        if name == "주차장":
            for i, ch in enumerate(name):
                px, py = P(x, y + i * 28)
                d.text((px, py), ch, font=Fnt(25), fill=(120, 55, 10), anchor="mm", stroke_width=4, stroke_fill=(255, 240, 220))
        elif name == "N":
            lab(x, y, "N", 17, (30, 30, 30))
        else:
            lab(x, y, name, 14, (40, 35, 40))
    out = tone_path.replace("tone_", "map_FINAL_").replace(".png", "_labeled.png")
    if out == tone_path:
        out = "map_FINAL_labeled.png"
    im.save(out); print("saved", out, im.size, "| scale f=%.3f" % f)


if __name__ == "__main__":
    main()
