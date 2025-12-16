"""OCR fallback for extracting mic queue from the Paltalk window.

Uses PIL ImageGrab (or mss) and pytesseract to OCR the mic-queue area when UIA can't read it.
This module is optional: if pytesseract or Tesseract binary is missing, the functions will return an explanatory error.
"""
from typing import List, Tuple, Optional
from PIL import Image, ImageOps, ImageFilter
import io


def _try_import_tesseract():
    try:
        import pytesseract
        return pytesseract
    except Exception as e:
        return None


def _preprocess(image):
    # Convert to grayscale, increase contrast, and threshold
    img = image.convert('L')
    img = ImageOps.autocontrast(img)
    img = img.filter(ImageFilter.SHARPEN)
    # Resize to improve OCR for small text
    w, h = img.size
    if h < 200:
        img = img.resize((int(w * 2), int(h * 2)), Image.LANCZOS)
    return img


def ocr_region(bbox: Tuple[int, int, int, int]) -> Tuple[Optional[List[str]], Optional[str]]:
    """Capture screen bbox and OCR it, returning list of lines or (None, error_msg)."""
    # Try to import PIL ImageGrab
    try:
        from PIL import ImageGrab
    except Exception as e:
        return None, f'Pillow ImageGrab not available: {e}'

    pyt = _try_import_tesseract()
    if pyt is None:
        return None, 'pytesseract not installed; run `pip install pytesseract` and ensure Tesseract is installed on PATH.'

    try:
        img = ImageGrab.grab(bbox=bbox)
    except Exception as e:
        return None, f'screenshot_failed: {e}'

    img = _preprocess(img)

    try:
        text = pyt.image_to_string(img, config='--psm 6')
    except Exception as e:
        return None, f'ocr_failed: {e}'

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return lines, None


def parse_mic_queue_lines(lines: List[str]) -> List[str]:
    """Heuristic parsing of OCR lines into usernames."""
    out = []
    noise_tokens = ('join', 'queue', 'talk', 'clear', 'mic', 'member', 'since', 'remove', 'ads')
    for ln in lines:
        l = ln.strip()
        if not l:
            continue
        low = l.lower()
        if any(tok in low for tok in noise_tokens):
            continue
        # split off numbering like '1 Gossip God' or '1. Gossip God'
        parts = l.split()
        if parts[0].rstrip('.').isdigit():
            name = ' '.join(parts[1:])
        else:
            name = l
        # drop if looks like an ad or long banner
        if len(name) > 40:
            continue
        out.append(name)
    # dedupe keeping order
    seen = set()
    res = []
    for n in out:
        if n not in seen:
            seen.add(n)
            res.append(n)
    return res
