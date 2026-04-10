"""Tests for the Pixel 8 Pro mockup generator.

Run with: pytest scripts/test_generate_mockup.py -v
(Requires Pillow: pip install pillow pytest)
"""
from pathlib import Path

import pytest
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
MOCKUP_PATH = REPO_ROOT / "mockup.png"


@pytest.fixture(scope="module")
def mockup() -> Image.Image:
    """Load mockup.png once for the whole test module."""
    assert MOCKUP_PATH.exists(), (
        f"mockup.png not found at {MOCKUP_PATH}. "
        "Run `python scripts/generate_mockup.py` first."
    )
    return Image.open(MOCKUP_PATH)


def test_mockup_dimensions(mockup: Image.Image) -> None:
    """Mockup must be exactly 1022x2148 per SKILL.md measurements."""
    assert mockup.size == (1022, 2148), f"unexpected size {mockup.size}"


def test_mockup_format(mockup: Image.Image) -> None:
    """Mockup must be an RGBA PNG so the screen area can be transparent."""
    assert mockup.format == "PNG", f"unexpected format {mockup.format}"
    assert mockup.mode == "RGBA", f"unexpected mode {mockup.mode}"


def test_mockup_screen_area_is_transparent(mockup: Image.Image) -> None:
    """The center of the image must be transparent so app screenshots show through.

    Per SKILL.md: screen top-left is (34, 34), width 954, height 2080.
    Center of screen area is approximately (511, 1074).
    """
    center_x, center_y = 511, 1074
    pixel = mockup.getpixel((center_x, center_y))
    assert len(pixel) == 4, f"expected RGBA tuple, got {pixel}"
    alpha = pixel[3]
    assert alpha < 50, (
        f"center pixel at ({center_x},{center_y}) should be transparent, "
        f"got alpha={alpha}"
    )


def test_mockup_bezel_is_opaque(mockup: Image.Image) -> None:
    """The top-left corner (bezel) must be opaque — that's the phone frame."""
    pixel = mockup.getpixel((5, 5))
    alpha = pixel[3]
    assert alpha > 200, (
        f"corner pixel should be opaque bezel, got alpha={alpha}"
    )


def test_mockup_bezel_is_dark(mockup: Image.Image) -> None:
    """The bezel should be a dark metallic color (per spec: #1a1a1a-#2a2a2a range)."""
    pixel = mockup.getpixel((5, 5))
    r, g, b, _a = pixel
    assert r < 80 and g < 80 and b < 80, (
        f"bezel should be dark, got rgb=({r},{g},{b})"
    )


def test_mockup_has_camera_cutout(mockup: Image.Image) -> None:
    """A hole-punch camera should exist near the top center.

    Camera cutout is ~24px diameter, ~48px from the top edge, centered horizontally.
    That places it near (511, 60). It should be dark/opaque (camera lens), NOT transparent.
    """
    pixel = mockup.getpixel((511, 60))
    alpha = pixel[3]
    assert alpha > 200, f"camera cutout should be opaque, got alpha={alpha}"
    r, g, b, _a = pixel
    assert r < 40 and g < 40 and b < 40, (
        f"camera cutout should be near-black, got rgb=({r},{g},{b})"
    )
