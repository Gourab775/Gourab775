#!/usr/bin/env python3
"""
Fetch the portrait source image from the internet (no local photo needed),
square-crop around the face and normalize contrast. Pillow only.
Output: source-photo.jpg, consumed by make_ascii_svg.py.
"""
import os
import urllib.request
from PIL import Image, ImageOps

URL = os.environ.get(
    "PORTRAIT_URL",
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80&auto=format&fit=crop",
)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "source-photo.jpg")

req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=60) as r:
    raw = r.read()
tmp = OUT + ".download"
with open(tmp, "wb") as f:
    f.write(raw)

im = Image.open(tmp).convert("RGB")
w, h = im.size
side = min(w, h)
cx, cy = w // 2, int(h * 0.42)
x0 = min(max(cx - side // 2, 0), w - side)
y0 = min(max(cy - side // 2, 0), h - side)
im = im.crop((x0, y0, x0 + side, y0 + side))
im = ImageOps.autocontrast(im, cutoff=1)
im.save(OUT, quality=92)
os.remove(tmp)
print("wrote", OUT, im.size)
