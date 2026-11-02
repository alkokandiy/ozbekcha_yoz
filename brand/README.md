# Brand

The logo is a serif wordmark with a quill — ink on cream paper. It reads as
writing and press rather than software, which is the right association for
the people this is for.

## Files

| File | Use |
|---|---|
| `logo-full.png` | The logo as delivered: textured card, soft shadow. Use it where a self-contained image is wanted — README header, GitHub social preview, a slide. |
| `lockup-ink.png` | Wordmark and quill as ink on a transparent background. For placing on your own surface. Invert it for dark backgrounds (`filter: invert(1)`). |
| `quill-ink.png` | The quill alone, for use as an accent or a divider. |
| `avatar.png`, `avatar.svg` | **Telegram avatar and anywhere circular.** The Ö alone, full-bleed. |
| `avatar-tile.svg` | The same mark as a rounded square, for a favicon or an app icon. |
| `favicon-32/96/192.png` | Raster favicons for hosts that will not take SVG. |
| `logo-prompt.md` | The prompt used to generate the mark, kept for regenerating variants. |

## Colours

| | Hex | |
|---|---|---|
| Ink | `#1A1816` | Not pure black. Printed ink never is. |
| Cream | `#F1EBDF` | The paper, sampled from the logo itself. |
| Paper | `#FAF6EC` | A half-step lighter, for cards sitting on the cream. |
| Accent | `#8A6A2F` | Warm brown, for the one small thing that must stand out. `#C9A86A` in dark mode. |

Monochrome on purpose. The logo earns its presence through the letterforms,
so colour has nothing to add and plenty to spoil.

## Why the avatar is not the logo

The lockup cannot be the Telegram avatar. Telegram crops to a circle at
roughly 40px, which cuts the corners off a square, removes the quill, and
reduces "Özbekça Yoz" to three grey smudges. A logo that is unreadable at
the size people actually see it is not doing its job.

So the avatar is **the Ö alone**, full-bleed, in the same ink on the same
cream. It is the one letter the whole project is about, it carries its own
diacritic, and it survives to 32px.

The quill was the other candidate. It loses: it is drawn in thin outline, and
below about 48px the lines go pale and the shape turns to fluff. It stays as
an accent, where its detail can be seen.

## One honest caveat

`avatar.svg` is the Ö rebuilt from two ellipses and two circles — a
high-contrast serif in the spirit of the wordmark, not a copy of its actual
typeface. Side by side at large sizes a typographer would see the difference
in the stroke modulation. At avatar size, nobody will.

If exactness matters later, export the Ö from the original font as outlines
and drop it in; the geometry in that file is a placeholder worth replacing,
not a decision to defend.

## Rules

- Do not recolour the mark. Ink on cream, or inverted. Nothing else.
- Do not put the lockup on a photograph or a busy background. It is a
  printed mark and wants a plain surface.
- Do not stretch the lockup, and do not re-set the wordmark in another font
  to make it fit — use `avatar.svg` when the space is tight.
- Keep the accent brown for one element at a time.
