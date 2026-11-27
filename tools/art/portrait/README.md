# The portrait (档案 page)

A pixel-art portrait drawn from the photo on his 履歴書, not a filtered photo:
the photo gives only where things are; the drawing is done here.

1. `seg.py` — reads `img-000.png` (`pdfimages -png <the PDF> img`), cuts the
   figure from its white ground and labels hair, skin, shirt, cardigan and tie.
2. `draw.py` — brings the labels down to 63×84 by majority vote, tidies them,
   and paints them in flat bands of a fixed palette, lit as in the compartment
   (the lamp on the right, the left in shadow, the tube's magenta along the
   left edge), with an outline and a dithered carriage-dark ground.
3. `features.py` — shades the face as a lit egg, sculpts the jaw, and draws the
   brows, eyes, nose, mouth and hair strands pixel by pixel.

Writes `portrait-art.png`; copy it to `public/assets/portrait.png`.

**In use now:** `public/assets/portrait.webp`, 543×724, generated with an AI
image tool from the 履歴書 photo in this style, chosen by him. The scripts
here made the earlier, hand-drawn version.
