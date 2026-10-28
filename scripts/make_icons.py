"""Tekent de app-iconen (radarbeeld) als PNG in app/pwa/icons/.

Gebruik: pip install pillow && python scripts/make_icons.py
De iconen staan in de repo; dit script is alleen nodig om ze opnieuw te maken.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "app" / "pwa" / "icons"
BG = (43, 69, 194)        # accentblauw uit de app (--accent)
FG = (255, 255, 255)
SIGNAL = (240, 176, 74)   # signaalgeel (--signal, donker thema)
SS = 4                    # supersampling voor gladde randen


def radar(size: int, content: float, rounded: bool) -> Image.Image:
    """content = deel van het vlak dat de radar vult (maskable: binnen de veilige zone)."""
    S = size * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if rounded:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=BG)
    else:
        d.rectangle([0, 0, S, S], fill=BG)
    c = S / 2
    r = S * content / 2
    w = max(2, int(S * 0.028))
    # zwaai (sector) van 12 uur naar ~2 uur
    sweep = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sweep).pieslice([c - r, c - r, c + r, c + r], start=-90, end=-30, fill=(255, 255, 255, 70))
    img.alpha_composite(sweep)
    for f, a in [(1.0, 150), (0.64, 110), (0.3, 90)]:
        rr = r * f
        ring = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse([c - rr, c - rr, c + rr, c + rr], outline=(255, 255, 255, a), width=w)
        img.alpha_composite(ring)
    ang = math.radians(-30)
    d = ImageDraw.Draw(img)
    d.line([c, c, c + r * 0.9 * math.cos(ang), c + r * 0.9 * math.sin(ang)], fill=FG, width=int(w * 1.6))
    d.ellipse([c - w * 1.6, c - w * 1.6, c + w * 1.6, c + w * 1.6], fill=FG)
    # signaal (geel) en een zwakkere blip
    bx, by = c + r * 0.55 * math.cos(math.radians(-55)), c + r * 0.55 * math.sin(math.radians(-55))
    br = r * 0.13
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=SIGNAL)
    sx, sy = c + r * 0.45 * math.cos(math.radians(140)), c + r * 0.45 * math.sin(math.radians(140))
    sr = r * 0.07
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 255, 255, 170))
    return img.resize((size, size), Image.LANCZOS)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    targets = {
        "icon-192.png": (192, 0.76, False),
        "icon-512.png": (512, 0.76, False),
        "icon-maskable-512.png": (512, 0.56, False),   # binnen de veilige zone (cirkel van 80%)
        "apple-touch-icon.png": (180, 0.72, False),
        "favicon-32.png": (32, 0.86, True),
    }
    for name, (size, content, rounded) in targets.items():
        im = radar(size, content, rounded)
        if not rounded:
            im = im.convert("RGB")  # volledig dekkend: geen transparante randen op Android
        im.save(OUT / name, optimize=True)
        print(name, im.size)


if __name__ == "__main__":
    main()
