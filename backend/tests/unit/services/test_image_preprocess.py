"""Unit tests for `app.services.image_preprocess.crop_and_resize`.

This service is pure in-memory image processing (Pillow only), so we run it
for real against synthetic images rather than mocking it.
"""

from io import BytesIO

import pytest
from PIL import Image

from app.services.image_preprocess import AVATAR_SIZE, crop_and_resize


def _png_bytes(width: int, height: int, color=(255, 0, 0, 255)) -> bytes:
    img = Image.new("RGBA", (width, height), color)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.unit
class TestCropAndResize:
    def test_output_is_avatar_size_square(self):
        raw = _png_bytes(400, 300)

        out = crop_and_resize(raw)

        img = Image.open(BytesIO(out))
        assert img.size == (AVATAR_SIZE, AVATAR_SIZE)
        assert img.format == "PNG"

    def test_output_is_avatar_size_even_when_input_is_portrait(self):
        raw = _png_bytes(100, 800)
        out = crop_and_resize(raw)
        img = Image.open(BytesIO(out))
        assert img.size == (AVATAR_SIZE, AVATAR_SIZE)

    def test_output_is_avatar_size_even_when_input_is_already_square(self):
        raw = _png_bytes(50, 50)
        out = crop_and_resize(raw)
        img = Image.open(BytesIO(out))
        assert img.size == (AVATAR_SIZE, AVATAR_SIZE)

    def test_accepts_jpeg_input(self):
        img = Image.new("RGB", (200, 200), (0, 255, 0))
        buf = BytesIO()
        img.save(buf, format="JPEG")

        out = crop_and_resize(buf.getvalue())

        result = Image.open(BytesIO(out))
        assert result.size == (AVATAR_SIZE, AVATAR_SIZE)
        assert result.format == "PNG"  # always re-encoded as PNG

    def test_raises_on_non_image_bytes(self):
        with pytest.raises(Exception):
            crop_and_resize(b"not an image")
