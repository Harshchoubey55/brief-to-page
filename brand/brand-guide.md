# Tidewell brand guide (v1)

Tidewell is a made-up advisory firm I use for practice work. This guide is the
reference the landing page is checked against. The same values live in
`src/css/tokens.css`, so if one changes the other has to change too.

## Colours

| Token            | Hex       | Use                                         |
| ---------------- | --------- | ------------------------------------------- |
| `--tw-navy`      | `#0B2545` | Headings, header, footer background         |
| `--tw-teal`      | `#13807A` | Primary buttons, links, key numbers         |
| `--tw-sand`      | `#F4EFE6` | Section backgrounds, cards                  |
| `--tw-coral`     | `#E4572E` | One accent per screen at most (badges)      |
| `--tw-ink`       | `#1D2733` | Body text                                   |
| `--tw-ink-muted` | `#5A6675` | Captions, helper text                       |
| `--tw-white`     | `#FFFFFF` | Text on navy, page background               |

Rules:

- Body text must reach 4.5:1 contrast against its background (WCAG AA).
- Coral is never used for body text or for anything a user must read to act.
- Teal on sand is allowed for buttons only at 18px bold or larger.

## Type

- Typeface: Source Sans 3 (self-hosted, weights 400 and 700 only).
- Fallback: `system-ui, "Segoe UI", Roboto, Arial, sans-serif`.

| Style   | Size (mobile / desktop) | Weight | Line height |
| ------- | ----------------------- | ------ | ----------- |
| H1      | 32px / 48px             | 700    | 1.15        |
| H2      | 26px / 34px             | 700    | 1.2         |
| H3      | 20px / 22px             | 700    | 1.3         |
| Body    | 17px / 18px             | 400    | 1.6         |
| Small   | 14px                    | 400    | 1.5         |

One H1 per page. Headings go in order, no skipping from H2 to H4.

## Spacing

An 8px scale: 4, 8, 16, 24, 32, 48, 64, 96. Section padding is 64px on mobile
and 96px on desktop. Content width tops out at 1120px.

## Images

- Flat illustration, brand colours only. No stock photos of people.
- Every image that carries meaning gets alt text that says what it shows, in
  under 125 characters. Decorative images get `alt=""`.
- Deliver as WebP with a JPEG fallback not needed (all target browsers read
  WebP). Widths: 480, 960, 1600.
- Every `<img>` has width and height set so the layout does not jump.

## Voice

Plain and specific. Say "costs rose 14%" rather than "unprecedented cost
headwinds". Avoid: "synergy", "leverage" (as a verb), "best-in-class",
"cutting-edge", "unlock".

Brand name is always "Tidewell", never "TideWell" or "Tidewell Advisory LLP".
