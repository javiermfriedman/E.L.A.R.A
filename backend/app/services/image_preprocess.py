from io import BytesIO
from PIL import Image
AVATAR_SIZE = 256


def crop_and_resize(raw_bytes: bytes) -> bytes:
    """Center-crop to a square, resize to AVATAR_SIZE×AVATAR_SIZE, return PNG bytes."""
    img = Image.open(BytesIO(raw_bytes))
    img = img.convert("RGBA")

    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    img = img.resize((AVATAR_SIZE, AVATAR_SIZE), Image.LANCZOS)

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()