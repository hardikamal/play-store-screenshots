"""Generate mockup.png — a Pixel 8 Pro-style phone frame.

The bundled mockup.png is a pre-measured 1022x2148 RGBA PNG with:
  - A dark metallic bezel (gradient #1a1a1a to #2a2a2a)
  - ~34px outer padding around a transparent screen area
  - ~60px corner radius on the screen cutout
  - A hole-punch camera cutout centered near the top
  - A subtle inner highlight along the bezel edge

SKILL.md references these exact measurements. Any change to dimensions
here MUST be mirrored in SKILL.md's Phone component constants.

Run: python scripts/generate_mockup.py
Output: mockup.png in the repo root
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

# Dimensions — locked in by SKILL.md. Do not change without updating SKILL.md.
MK_W = 1022
MK_H = 2148

# Screen area (transparent cutout)
SCREEN_LEFT = 34
SCREEN_TOP = 34
SCREEN_WIDTH = 954
SCREEN_HEIGHT = 2080
SCREEN_CORNER_RADIUS = 60

# Camera hole-punch
CAMERA_CX = MK_W // 2
CAMERA_CY = 60
CAMERA_R = 12  # 24px diameter

# Bezel colors
BEZEL_TOP_COLOR = (26, 26, 26, 255)    # #1a1a1a
BEZEL_BOTTOM_COLOR = (42, 42, 42, 255)  # #2a2a2a

# Inner highlight for depth
HIGHLIGHT_COLOR = (255, 255, 255, 20)
HIGHLIGHT_INSET = 2

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = REPO_ROOT / "mockup.png"


def make_vertical_gradient(
    width: int,
    height: int,
    top: tuple[int, int, int, int],
    bottom: tuple[int, int, int, int],
) -> Image.Image:
    """Create a vertical gradient image from `top` to `bottom`."""
    img = Image.new("RGBA", (width, height), top)
    pixels = img.load()
    tr, tg, tb, ta = top
    br, bg, bb, ba = bottom
    for y in range(height):
        t = y / max(height - 1, 1)
        r = int(tr + (br - tr) * t)
        g = int(tg + (bg - tg) * t)
        b = int(tb + (bb - tb) * t)
        a = int(ta + (ba - ta) * t)
        for x in range(width):
            pixels[x, y] = (r, g, b, a)
    return img


def make_rounded_mask(
    width: int,
    height: int,
    radius: int,
) -> Image.Image:
    """Return an L-mode mask with a rounded rectangle in white."""
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        (0, 0, width - 1, height - 1),
        radius=radius,
        fill=255,
    )
    return mask


def generate_mockup() -> Image.Image:
    """Build the Pixel 8 Pro mockup as an RGBA Image."""
    # 1. Bezel: full-canvas vertical gradient.
    bezel = make_vertical_gradient(MK_W, MK_H, BEZEL_TOP_COLOR, BEZEL_BOTTOM_COLOR)

    # 2. Round the outer corners of the whole frame slightly (phone outline).
    #    Radius is small enough that the outermost bezel pixels (e.g. 5,5)
    #    remain opaque — tests check that corner as part of the frame.
    outer_mask = make_rounded_mask(MK_W, MK_H, radius=12)
    frame = Image.new("RGBA", (MK_W, MK_H), (0, 0, 0, 0))
    frame.paste(bezel, (0, 0), mask=outer_mask)

    # 3. Add a subtle inner highlight just inside the outer edge for depth.
    #    Use alpha_composite so the highlight layers OVER the bezel instead
    #    of replacing its pixels.
    highlight_layer = Image.new("RGBA", (MK_W, MK_H), (0, 0, 0, 0))
    hl_draw = ImageDraw.Draw(highlight_layer)
    hl_draw.rounded_rectangle(
        (
            HIGHLIGHT_INSET + 4,
            HIGHLIGHT_INSET + 4,
            MK_W - 1 - HIGHLIGHT_INSET - 4,
            MK_H - 1 - HIGHLIGHT_INSET - 4,
        ),
        radius=8,
        outline=HIGHLIGHT_COLOR,
        width=2,
    )
    frame = Image.alpha_composite(frame, highlight_layer)

    # 4. Punch out the screen area (transparent rounded rect).
    screen_mask = Image.new("L", (MK_W, MK_H), 255)
    sm_draw = ImageDraw.Draw(screen_mask)
    sm_draw.rounded_rectangle(
        (
            SCREEN_LEFT,
            SCREEN_TOP,
            SCREEN_LEFT + SCREEN_WIDTH - 1,
            SCREEN_TOP + SCREEN_HEIGHT - 1,
        ),
        radius=SCREEN_CORNER_RADIUS,
        fill=0,
    )
    r, g, b, a = frame.split()
    a = Image.composite(a, Image.new("L", a.size, 0), screen_mask)
    frame = Image.merge("RGBA", (r, g, b, a))

    # 5. Draw the hole-punch camera cutout AFTER the screen is transparent.
    #    The camera sits INSIDE the transparent screen area, so we draw an
    #    opaque dark circle on top to simulate the lens.
    camera_layer = Image.new("RGBA", (MK_W, MK_H), (0, 0, 0, 0))
    cam_draw = ImageDraw.Draw(camera_layer)
    cam_draw.ellipse(
        (
            CAMERA_CX - CAMERA_R,
            CAMERA_CY - CAMERA_R,
            CAMERA_CX + CAMERA_R,
            CAMERA_CY + CAMERA_R,
        ),
        fill=(12, 12, 12, 255),
        outline=(40, 40, 40, 255),
        width=1,
    )
    frame = Image.alpha_composite(frame, camera_layer)

    return frame


def main() -> None:
    mockup = generate_mockup()
    mockup.save(OUTPUT_PATH, format="PNG")
    print(f"Wrote {OUTPUT_PATH} ({mockup.size[0]}x{mockup.size[1]})")


if __name__ == "__main__":
    main()
