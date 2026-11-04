"""Draw the placeholder illustrations for the page.

I didn't have real campaign artwork, so these are simple flat drawings in the
brand colours. They are saved as large PNGs on purpose, the way files usually
arrive from a designer, so the image step has something real to work on.

    python scripts/make_placeholder_art.py
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent.parent / "assets" / "originals"

NAVY = (11, 37, 69)
TEAL = (19, 128, 122)
SAND = (244, 239, 230)
CORAL = (228, 87, 46)
INK = (29, 39, 51)


def grain(img, amount=10, seed=0):
    """Add light paper grain. Makes the PNG heavier, like a real export."""
    rnd = random.Random(seed)
    px = img.load()
    w, h = img.size
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            n = rnd.randint(-amount, amount)
            r, g, b = px[x, y]
            px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)))
    return img


def sky(draw, w, h, top, bottom):
    for y in range(h):
        t = y / h
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(0, y), (w, y)], fill=c)


def container(draw, x, y, cw, ch, colour):
    draw.rectangle([x, y, x + cw, y + ch], fill=colour)
    for i in range(1, 6):
        lx = x + i * cw // 6
        draw.line([(lx, y + 6), (lx, y + ch - 6)], fill=tuple(max(0, c - 30) for c in colour), width=4)


def hero(w=2800, h=1600):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    sky(d, w, h, (18, 52, 92), (232, 150, 110))
    d.ellipse([w * 0.68, h * 0.18, w * 0.68 + 260, h * 0.18 + 260], fill=(250, 214, 170))
    # water
    d.rectangle([0, h * 0.72, w, h], fill=(16, 72, 96))
    for i in range(40):
        y = h * 0.74 + i * 11
        d.line([(random.randint(0, w), y), (random.randint(0, w), y)], fill=(40, 110, 130), width=3)
    # quay and cranes
    d.rectangle([0, h * 0.64, w * 0.62, h * 0.72], fill=INK)
    for cx in (300, 900, 1500):
        d.rectangle([cx, h * 0.22, cx + 40, h * 0.64], fill=CORAL)
        d.rectangle([cx - 260, h * 0.22, cx + 420, h * 0.22 + 36], fill=CORAL)
        d.line([(cx + 20, h * 0.22), (cx - 200, h * 0.40)], fill=CORAL, width=8)
    colours = [TEAL, NAVY, CORAL, SAND, TEAL, NAVY]
    for row in range(3):
        for col in range(9):
            container(d, 80 + col * 190, int(h * 0.64) - (row + 1) * 90, 180, 84,
                      colours[(row + col) % len(colours)])
    # ship
    d.polygon([(1800, h * 0.70), (2700, h * 0.70), (2620, h * 0.80), (1860, h * 0.80)], fill=NAVY)
    for col in range(6):
        container(d, 1880 + col * 125, int(h * 0.70) - 80, 118, 76, colours[col % len(colours)])
    img = img.filter(ImageFilter.SMOOTH)
    return grain(img, seed=1)


def scene(kind, w=2400, h=1600):
    img = Image.new("RGB", (w, h), SAND)
    d = ImageDraw.Draw(img)
    d.rectangle([0, h * 0.78, w, h], fill=(226, 216, 199))
    if kind == "suppliers":
        # two factories joined by a route
        for fx, colour in ((260, NAVY), (1500, TEAL)):
            d.rectangle([fx, 620, fx + 620, 1250], fill=colour)
            for i in range(3):
                d.polygon([(fx + i * 206, 620), (fx + i * 206 + 206, 620), (fx + i * 206 + 206, 480)], fill=colour)
            d.rectangle([fx + 440, 300, fx + 520, 620], fill=colour)
        d.line([(880, 1000), (1500, 1000)], fill=CORAL, width=18)
        d.polygon([(1460, 960), (1500, 1000), (1460, 1040)], fill=CORAL)
    elif kind == "freight":
        # truck on a road with a rising price line behind it
        d.line([(200, 1100), (700, 900), (1200, 950), (1700, 600), (2200, 380)], fill=CORAL, width=22)
        d.rectangle([600, 1050, 1500, 1350], fill=TEAL)
        d.rectangle([1500, 1150, 1850, 1350], fill=NAVY)
        for wx in (720, 1100, 1650):
            d.ellipse([wx, 1300, wx + 150, 1450], fill=INK)
    else:
        # shelving with boxes
        for sy in (520, 860, 1200):
            d.rectangle([300, sy, 2100, sy + 30], fill=NAVY)
            for bx in range(330, 2050, 230):
                bh = random.randint(160, 280)
                d.rectangle([bx, sy - bh, bx + 200, sy], fill=random.choice([TEAL, CORAL, (196, 160, 110)]))
        for px_ in (300, 2070):
            d.rectangle([px_, 300, px_ + 30, 1250], fill=NAVY)
    img = img.filter(ImageFilter.SMOOTH)
    return grain(img, seed=len(kind))


def main():
    random.seed(7)
    OUT.mkdir(parents=True, exist_ok=True)
    hero().save(OUT / "hero-harbour.png", optimize=False)
    for kind in ("suppliers", "freight", "stock"):
        scene(kind).save(OUT / f"theme-{kind}.png", optimize=False)
    for f in sorted(OUT.glob("*.png")):
        print(f"{f.name}: {f.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
