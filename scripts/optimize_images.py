"""Turn the original PNGs into WebP files in the sizes the page uses.

For every file in assets/originals/ this writes <name>-480.webp, -960.webp and
-1600.webp into src/images/ (never upscaling), plus src/images/manifest.json
with the sizes, which the build uses for srcset and width/height.

    python scripts/optimize_images.py
"""
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "originals"
OUT = ROOT / "src" / "images"
WIDTHS = [480, 960, 1600]
QUALITY = 80


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {}
    total_before = total_after = 0

    for original in sorted(SRC.glob("*.png")):
        name = original.stem
        img = Image.open(original).convert("RGB")
        w, h = img.size
        total_before += original.stat().st_size

        files = []
        for target in WIDTHS:
            if target > w:
                continue
            resized = img.resize((target, round(h * target / w)), Image.LANCZOS)
            path = OUT / f"{name}-{target}.webp"
            resized.save(path, "WEBP", quality=QUALITY, method=6)
            files.append({"file": path.name, "width": target, "bytes": path.stat().st_size})

        manifest[name] = {"width": w, "height": h, "sizes": files}
        mid = files[min(1, len(files) - 1)]
        total_after += mid["bytes"]
        print(f"{name}: {original.stat().st_size // 1024} KB png -> "
              + ", ".join(f"{f['width']}w {f['bytes'] // 1024} KB" for f in files))

    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"\noriginals {total_before // 1024} KB, 960w set {total_after // 1024} KB")


if __name__ == "__main__":
    main()
