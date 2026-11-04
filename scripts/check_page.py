"""Pre-publish checklist for the built page.

Runs the checks I'd otherwise do by hand before a page goes live: images,
headings, form labels, metadata, links, and whether the CSS still matches the
brand guide. Prints a list and exits with 1 if anything is an error.

    python scripts/check_page.py            # checks docs/index.html
    python scripts/check_page.py --strict   # warnings count as errors too
"""
import argparse
import json
import re
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "docs"

MAX_IMAGE_KB = 300
MAX_ALT_CHARS = 125
BANNED_WORDS = ["synergy", "leverage", "best-in-class", "cutting-edge", "unlock"]
BRAND_NAME = "Tidewell"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images, self.headings, self.inputs, self.labels = [], [], [], set()
        self.ids, self.links, self.assets, self.meta = set(), [], [], {}
        self.lang = None
        self.title = ""
        self.text = []
        self._in_title = False
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "title":
            self._in_title = True
        elif tag in ("script", "style"):
            self._skip += 1
            if a.get("src"):
                self.assets.append(a["src"])
        elif tag == "meta" and "name" in a:
            self.meta[a["name"]] = a.get("content", "")
        elif tag == "link" and a.get("href"):
            self.assets.append(a["href"])
        elif tag == "img":
            self.images.append(a)
            if a.get("src"):
                self.assets.append(a["src"])
        elif tag == "source" and a.get("srcset"):
            self.assets.extend(part.split()[0] for part in a["srcset"].split(","))
        elif re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        elif tag == "input" and a.get("type") not in ("hidden", "submit"):
            self.inputs.append(a)
        elif tag == "label" and a.get("for"):
            self.labels.add(a["for"])
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag in ("script", "style"):
            self._skip -= 1

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif not self._skip:
            self.text.append(data)


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def contrast(fg, bg):
    def lum(c):
        out = []
        for v in hex_to_rgb(c):
            v /= 255
            out.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
        return 0.2126 * out[0] + 0.7152 * out[1] + 0.0722 * out[2]
    a, b = sorted((lum(fg), lum(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def brand_colours_from_guide():
    guide = (ROOT / "brand" / "brand-guide.md").read_text(encoding="utf-8")
    return {m[0]: m[1].upper() for m in re.findall(r"`(--tw-[\w-]+)`\s*\|\s*`(#[0-9A-Fa-f]{6})`", guide)}


def brand_colours_from_css():
    css = (ROOT / "src" / "css" / "tokens.css").read_text(encoding="utf-8")
    return {m[0]: m[1].upper() for m in re.findall(r"(--tw-[\w-]+):\s*(#[0-9A-Fa-f]{6})", css)}


def run_checks():
    errors, warnings = [], []
    html = (SITE / "index.html").read_text(encoding="utf-8")
    p = PageParser()
    p.feed(html)

    # images
    for img in p.images:
        src = img.get("src", "?")
        if "alt" not in img:
            errors.append(f"image {src}: no alt attribute")
        elif len(img["alt"]) > MAX_ALT_CHARS:
            warnings.append(f"image {src}: alt text is {len(img['alt'])} chars, keep it under {MAX_ALT_CHARS}")
        if not (img.get("width") and img.get("height")):
            errors.append(f"image {src}: width/height not set, layout will shift while it loads")
        f = SITE / src
        if f.exists() and f.stat().st_size > MAX_IMAGE_KB * 1024:
            errors.append(f"image {src}: {f.stat().st_size // 1024} KB, budget is {MAX_IMAGE_KB} KB")
        if not src.endswith(".webp"):
            warnings.append(f"image {src}: not WebP")

    # headings
    if p.headings.count(1) != 1:
        errors.append(f"page has {p.headings.count(1)} h1 elements, needs exactly one")
    for prev, cur in zip(p.headings, p.headings[1:]):
        if cur > prev + 1:
            errors.append(f"heading jumps from h{prev} to h{cur}")

    # form
    for inp in p.inputs:
        if inp.get("id") not in p.labels:
            errors.append(f"form field '{inp.get('name')}' has no visible <label>")

    # metadata
    if not p.lang:
        errors.append("<html> has no lang attribute")
    if not 10 <= len(p.title.strip()) <= 60:
        warnings.append(f"title is {len(p.title.strip())} chars, aim for 10-60")
    desc = p.meta.get("description", "")
    if not 50 <= len(desc) <= 160:
        errors.append(f"meta description is {len(desc)} chars, needs 50-160")

    content = json.loads((ROOT / "content" / "page.json").read_text(encoding="utf-8"))
    for field in ("owner", "review_date", "tags"):
        if not content["meta"].get(field):
            errors.append(f"page.json meta.{field} is empty")
    review = content["meta"].get("review_date")
    if review and date.fromisoformat(review) <= date.today():
        warnings.append(f"review date {review} has passed, page needs a content review")

    # links and files
    for href in p.links:
        if href.startswith("#") and href[1:] not in p.ids:
            errors.append(f"link {href} points to an id that isn't on the page")
    for asset in p.assets:
        if not re.match(r"https?:|data:|//", asset) and not (SITE / asset).exists():
            errors.append(f"missing file: {asset}")

    # brand
    guide, css = brand_colours_from_guide(), brand_colours_from_css()
    for name, hexval in guide.items():
        if css.get(name) != hexval:
            errors.append(f"tokens.css {name} is {css.get(name)}, brand guide says {hexval}")
    for fg in ("--tw-ink", "--tw-ink-muted"):
        for bg in ("--tw-white", "--tw-sand"):
            if fg in css and bg in css:
                ratio = contrast(css[fg], css[bg])
                if ratio < 4.5:
                    errors.append(f"{fg} on {bg} contrast is {ratio:.2f}:1, needs 4.5:1")

    text = " ".join(p.text)
    for word in BANNED_WORDS:
        if re.search(rf"\b{re.escape(word)}\b", text, re.I):
            warnings.append(f"off-brand word in copy: '{word}'")
    for wrong in set(re.findall(r"\btide\s?well\b", text, re.I)) - {BRAND_NAME}:
        errors.append(f"brand name written as '{wrong}', should be '{BRAND_NAME}'")

    return errors, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="fail on warnings too")
    args = ap.parse_args()

    errors, warnings = run_checks()
    for e in errors:
        print(f"ERROR  {e}")
    for w in warnings:
        print(f"WARN   {w}")
    print(f"\n{len(errors)} errors, {len(warnings)} warnings")

    if errors or (args.strict and warnings):
        sys.exit(1)


if __name__ == "__main__":
    main()
