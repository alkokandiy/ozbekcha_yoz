# Brand

| File | Use |
|---|---|
| `logo-mark.svg` | Telegram avatar, circular contexts. Full-bleed circle — Telegram crops to a circle anyway, so there is no padding to fight. |
| `logo-mark-tile.svg` | GitHub, favicon, anywhere square. Same mark, rounded square. |
| `logo-wordmark.svg` | Horizontal lockup for the README, a web page header, or a channel banner. |

## Colours

| | Hex | Role |
|---|---|---|
| Teal | `#11857F` | The mark. Samarkand tile blue-green, dark enough for white text on it. |
| Cream | `#F7F1E3` | The letter. Not pure white — paper, not screen. |
| Gold | `#D9A441` | The diacritic only. Never more than the two dots. |

All three read in light and dark mode, which is why the mark carries its own
background rather than inheriting the page's.

## The idea

The letter is drawn, not typed: the **Ö** is a ring, and its umlaut is two
eight-pointed stars — the geometry that is on every tiled façade in
Samarkand and Bukhara, at the one spot in the letter where the new alphabet
differs from the old. The diacritic *is* the product, so the diacritic is the
only thing in gold.

At 40px the stars stop being stars and read as two dots, which is the correct
failure: the mark degrades into a legible Ö rather than into mud.

## Rules

- The gold is for diacritics. Never fill the ring with it, never use it for text.
- Do not add a stroke or a shadow to the mark. It is flat on purpose.
- Do not stretch the lockup. If it needs to be narrower, stack the wordmark
  under the mark instead.
- The wordmark's text is live text. Convert it to outlines before using the
  file anywhere the font will not be available — a web page may keep it live.
