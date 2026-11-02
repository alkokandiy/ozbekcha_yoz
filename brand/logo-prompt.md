# Prompt for an AI logo generator

## Use the symbol only

Image generators cannot draw letterforms reliably — `Ö` comes back as `O`,
`Q`, or a glyph that exists in no alphabet, and the two dots land crooked.
So ask for **the symbol alone, with no text in the image.** The wordmark gets
set in vector afterwards, where the diacritics are exact.

If a tool insists on including text, generate it anyway and ignore the
lettering; only the mark matters.

## Main prompt

```
Minimalist flat vector logo mark for an Uzbek language tool. A single bold
geometric symbol: a thick open ring, like the letter O, with two small
eight-pointed Islamic stars sitting above it where an umlaut would be.
Inspired by Samarkand ceramic tilework and Timurid geometry — clean, exact,
symmetrical. Deep teal background, cream ring, gold stars. Three colours
only. Perfectly centred in a circle. Flat 2D, hard edges, no gradients, no
shading, no outline strokes, no texture. Reads clearly at 32 pixels. Vector
logo, app icon, solid background.
```

## Variants worth trying

Swap the second sentence for one of these and keep everything else:

```
A pointed Timurid arch, drawn as a single thick stroke, with two small
eight-pointed stars above its apex.
```

```
An eight-pointed Islamic star made of two overlapping squares, with a thick
open ring nested inside it.
```

```
Two concentric rings broken by a single gap at the top, with two small square
dots floating above the gap.
```

## Negative prompt

```
text, letters, words, typography, calligraphy, serif, script, gradient,
drop shadow, 3d, bevel, emboss, glow, neon, photorealistic, mascot, face,
animal, mosque, minaret, flag, cotton plant, busy pattern, ornate border,
many colours, thin hairlines, watermark, signature, frame
```

## Colours to give it, if the tool takes hex

| | Hex |
|---|---|
| Teal background | `#11857F` |
| Cream ring | `#F7F1E3` |
| Gold diacritic | `#D9A441` |

Keep the gold on the diacritic alone. The two dots are the whole idea — they
are the one place the new alphabet differs from the old — so nothing else in
the mark should compete with them for attention.

## What to check before choosing one

1. **Shrink it to 32px.** Most AI logos die here. If it turns to mud, it is
   not usable as a Telegram avatar, whatever it looks like at full size.
2. **Count the colours.** More than three means it will not reproduce cleanly
   in one colour, on a stamp, or embroidered.
3. **Look for thin lines.** Anything under about 1/20th of the width will
   vanish when scaled down.
4. **Check it is symmetrical.** AI output is often a few pixels off, which
   looks like a mistake rather than a style.

Send me the file you pick — PNG is fine. I will trace it to clean vector and
produce the circular avatar, the square tile and the horizontal wordmark from
it, with the lettering set properly.
