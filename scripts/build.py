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

    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=True,
        undefined=StrictUndefined,  # a missing field in page.json should fail the build
        trim_blocks=True,
        lstrip_blocks=True,
    )
    html = env.get_template("base.html").render(**content)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / "index.html").write_text(html, encoding="utf-8")

    copy_tree(ROOT / "src" / "css", OUT / "css")
    copy_tree(ROOT / "src" / "fonts", OUT / "fonts")
    copy_tree(ROOT / "src" / "js", OUT / "js")
    shutil.copy2(ROOT / "src" / "vendor" / "jquery-3.7.1.min.js", OUT / "js")
    copy_tree(ROOT / "assets" / "originals", OUT / "images")

    print(f"built {OUT / 'index.html'}")


if __name__ == "__main__":
    main()
