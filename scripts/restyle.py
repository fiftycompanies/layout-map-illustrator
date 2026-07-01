#!/usr/bin/env python3
"""3단계: 정확본(base_blank)을 저 톤으로 "덧칠"만.

Nano Banana Pro(gemini-3-pro-image-preview)에 base_blank를 참조로 넣고
스타일만 리페인트(위치·구도 유지, 글씨 제거). 톤: watercolor | cartoon.

필요: GOOGLE_API_KEY 환경변수 + `pip install google-genai`
      (blog-insta-auto backend/.venv 에 이미 설치돼 있음 → 그 파이썬으로 실행)
사용: GOOGLE_API_KEY=... python restyle.py base_blank.png --tone cartoon --n 2
"""
import sys, os, base64

TONES = {
    "watercolor": "soft warm HAND-PAINTED WATERCOLOR — gentle washes, subtle paper texture, hand-painted edges",
    "cartoon":    "clean warm HAND-DRAWN CARTOON illustration — soft cel shading, clean rounded ink outlines, cozy, cute little trees",
}


def build_prompt(tone):
    return (
        f"Repaint THIS campground map in a {TONES[tone]} style. "
        "KEEP the EXACT same composition, framing, size, boundary, all roads, the river, the orange parking strip, "
        "buildings, trees, and the EXACT position/size/color of every colored site box. "
        "Do NOT move, resize, add, or remove anything. Keep site boxes as clean solid colored rounded boxes, BLANK. "
        "Remove ALL leftover text — the image must have ZERO text/labels; I will add labels afterward. "
        "Style repaint only, not a redraw."
    )


def main():
    src = sys.argv[1]
    tone = sys.argv[sys.argv.index("--tone")+1] if "--tone" in sys.argv else "cartoon"
    n = int(sys.argv[sys.argv.index("--n")+1]) if "--n" in sys.argv else 2
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    prompt = build_prompt(tone)
    import PIL.Image
    ref = PIL.Image.open(src)
    for i in range(1, n+1):
        resp = client.models.generate_content(
            model="gemini-3-pro-image-preview", contents=[prompt, ref],
            config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]))
        for part in resp.candidates[0].content.parts:
            data = getattr(getattr(part, "inline_data", None), "data", None)
            if data:
                if isinstance(data, str):
                    data = base64.b64decode(data)
                out = f"tone_{tone}_{i}.png"; open(out, "wb").write(data); print("saved", out, len(data))
                break


if __name__ == "__main__":
    main()
