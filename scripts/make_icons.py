"""Tekent de app-iconen (radar, variant B 'Signaal') als PNG in app/pwa/icons/.

Ontwerp (31-10-2026): zwarte achtergrond van de app, twee lichte ringen, een volle oranje
zwaai (de accentkleur van de Radar) en een witte stip als 'gevonden signaal'.
Het logo in de kop van de app (app/index.html, svg.mark) is hetzelfde ontwerp.

Gebruik: pip install pillow && python scripts/make_icons.py
De iconen staan in de repo; dit script is alleen nodig om ze opnieuw te maken.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "app" / "pwa" / "icons"
BG = (15, 18, 23)          # --bg
RING = (196, 203, 214)     # lichte ring
RING2 = (128, 137, 152)    # binnenring
SWEEP = (240, 176, 74)     # --accent2 (oranje)
DOT = (231, 234, 240)      # --ink
SS = 4                     # supersampling voor gladde randen


def radar(size: int, content: float) -> Image.Image:
    """content = deel van het vlak dat de radar vult (maskable: binnen de veilige zone)."""
    S = size * SS
    img = Image.new("RGBA", (S, S), BG + (255,))
    c, r = S / 2, S * content / 2
    w = max(2, int(S * (0.045 if size >= 64 else 0.06)))

    def layer(draw_fn):
        l = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        draw_fn(ImageDraw.Draw(l))
        img.alpha_composite(l)

    layer(lambda d: d.pieslice([c - r, c - r, c + r, c + r], -90, -20, fill=SWEEP))
    layer(lambda d: d.ellipse([c - r, c - r, c + r, c + r], outline=RING, width=w))
    if size >= 48:  # op heel klein formaat alleen de buitenring
        ri = r * 0.55
        layer(lambda d: d.ellipse([c - ri, c - ri, c + ri, c + ri], outline=RING2, width=w))
    d = ImageDraw.Draw(img)
    a = math.radians(-55)
    bx, by, br = c + r * 0.72 * math.cos(a), c + r * 0.72 * math.sin(a), r * 0.14
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=DOT)
    d.ellipse([c - w * 1.1, c - w * 1.1, c + w * 1.1, c + w * 1.1], fill=DOT)
    return img.resize((size, size), Image.LANCZOS).convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    targets = {
        "icon-192.png": (192, 0.80),
        "icon-512.png": (512, 0.80),
        "icon-maskable-512.png": (512, 0.62),   # binnen de veilige zone (cirkel van 80%)
        "apple-touch-icon.png": (180, 0.76),
        "favicon-32.png": (32, 0.92),
    }
    for name, (size, content) in targets.items():
        im = radar(size, content)
        im.save(OUT / name, optimize=True)
        print(name, im.size)


if __name__ == "__main__":
    main()
