# brief-to-page

A campaign landing page built from a written brief and a small brand guide,
then fixed until it passed a pre-publish checklist and Lighthouse.

I wanted to practise the day-to-day of web content work: take a brief and some
assets, build the page from reusable parts, keep the copy separate from the
code, and check the result against brand and accessibility rules before it
goes live. The brand (Tidewell) is made up and the figures on the page are
sample content.

**Live page:** https://harshchoubey55.github.io/brief-to-page/

## Results

Lighthouse, mobile preset, median of 3 runs. The first build is tagged
`first-pass`; full reports are in `reports/lighthouse/`.

|                         | First build | After fixes |
| ----------------------- | ----------- | ----------- |
| Performance             | 74          | 100         |
| Accessibility           | 90          | 100         |
| Best practices          | 96          | 100         |
| SEO                     | 91          | 100         |
| Largest contentful paint| 22.4 s      | 1.9 s       |
| Page weight             | 4,026 KiB   | 164 KiB     |
| `check_page.py` errors  | 16          | 0           |

What made the difference:

- **Images.** The illustrations came in as 0.9-1.2 MB PNGs. `optimize_images.py`
  makes WebP copies at 480, 960 and 1600 px, and the page picks one with
  `srcset`. Each image also got width and height so nothing jumps while loading.
- **Alt text.** Two illustrations had none. Added it to `page.json`.
- **Contrast.** I had used a lighter grey for helper text than the brand guide
  allows (3.0:1). Put it back to the brand value (5.9:1). Lighthouse also
  caught coral text on navy (4.2:1), which the brand guide already rules out,
  so I added that rule to the checker as well.
- **Form labels.** The first form used placeholders as labels. They disappear
  once you start typing, so the fields now have real `<label>`s.
- **Loading.** Scripts are deferred, fonts are preloaded and use
  `font-display: swap`.
- **One bug the scores exposed:** setting width/height on the hero image without
  `height: auto` in the CSS stretched it on phones.

Two things Lighthouse still lists as savings are server settings (gzip and
cache headers) that the local test server doesn't send; GitHub Pages does.

## How it fits together

```
brief/landing-page-brief.docx   what was asked for
brand/brand-guide.md            colours, type, spacing, image and voice rules
content/page.json               all copy, alt text and page metadata (owner, review date, tags)
templates/                      base page + one file per section (hero, stats, cards, faq, form...)
src/css/tokens.css              brand values as CSS variables
src/js/main.js                  jQuery: mobile menu, FAQ accordion, form validation
assets/originals/               images as received
scripts/
  optimize_images.py            originals -> WebP sizes + manifest
  build.py                      page.json + templates -> docs/index.html
  check_page.py                 pre-publish checklist
  lighthouse.sh                 3 Lighthouse runs, keeps the median
  make_placeholder_art.py       draws the placeholder illustrations
docs/                           built site (served by GitHub Pages)
reports/                        checklist output and Lighthouse reports, before and after
```

Copy changes only touch `content/page.json`. A new report page would reuse the
same templates with a new JSON file.

## What the checker looks at

`scripts/check_page.py` reads the built page and fails if any of these are off:

- every image has an alt attribute, width and height, is WebP and under 300 KB
- one `h1`, and headings don't skip levels
- every form field has a visible label
- page has a `lang`, a title and a 50-160 character meta description
- `page.json` has an owner, tags and a review date (warns when the date has passed)
- `#anchor` links point at real ids and every local file the page loads exists
- colours in `tokens.css` match the brand guide, text colours reach 4.5:1
  contrast, and coral is never used as a text colour
- the copy avoids the words the brand guide bans, and spells "Tidewell" right

## Running it

Python 3.10+.

```bash
pip install -r requirements.txt
python scripts/optimize_images.py   # only needed when images change
python scripts/build.py
python scripts/check_page.py
python -m http.server 8000 --directory docs
```

Lighthouse needs Node and Chrome:

```bash
./scripts/lighthouse.sh final
```

## Notes

- jQuery 3.7.1 and Source Sans 3 (SIL Open Font License, see `src/fonts/OFL.txt`)
  are vendored so the page has no outside requests.
- The form only validates input and shows a message. Nothing is sent anywhere.
