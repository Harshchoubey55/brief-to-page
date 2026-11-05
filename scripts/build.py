"""Build the landing page from content/page.json and the templates.

Output goes to docs/ so GitHub Pages can serve it straight from the repo.

    python scripts/build.py
"""
import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"


def copy_tree(src, dst):
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.iterdir():
        if f.is_file():
            shutil.copy2(f, dst / f.name)


def main():
    content = json.loads((ROOT / "content" / "page.json").read_text(encoding="utf-8"))
    # written by scripts/optimize_images.py
    images = json.loads((ROOT / "src" / "images" / "manifest.json").read_text(encoding="utf-8"))

    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=True,
        undefined=StrictUndefined,  # a missing field in page.json should fail the build
        trim_blocks=True,
        lstrip_blocks=True,
    )
    html = env.get_template("base.html").render(images=images, **content)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / "index.html").write_text(html, encoding="utf-8")
    # docs/ is already a finished site, so GitHub Pages doesn't need to run Jekyll on it
    (OUT / ".nojekyll").touch()

    for folder in ("css", "fonts", "js"):
        copy_tree(ROOT / "src" / folder, OUT / folder)
    shutil.copy2(ROOT / "src" / "vendor" / "jquery-3.7.1.min.js", OUT / "js")
    shutil.copy2(ROOT / "src" / "favicon.svg", OUT)
    copy_tree(ROOT / "src" / "images", OUT / "images")
    (OUT / "images" / "manifest.json").unlink()

    print(f"built {OUT / 'index.html'}")


if __name__ == "__main__":
    main()
