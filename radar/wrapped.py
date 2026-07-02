"""Monthly "Radar Wrapped" — a shareable PNG report card, Spotify-Wrapped style.

`site/wrapped/{YYYY-MM}.png` (+ a `latest.png` copy) is rendered with Pillow
from that month's releases. `ensure_current()` builds last month's card if it
doesn't exist yet — called from refresh, fail-soft.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone

from .build_site import SITE_DIR, SITE_JSON

WRAPPED_DIR = SITE_DIR / "wrapped"

BG = (11, 13, 23)
CYAN = (34, 211, 238)
PURPLE = (124, 92, 255)
GREEN = (94, 230, 168)
MUTED = (154, 160, 189)
WHITE = (231, 233, 243)

_FONT_CANDIDATES = [
    "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",  # Windows
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",           # CI (Ubuntu)
]
_FONT_REG = [
    "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _font(size: int, bold: bool = True):
    from PIL import ImageFont

    for path in (_FONT_CANDIDATES if bold else _FONT_REG):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _month_label(ym: str) -> str:
    return datetime.strptime(ym, "%Y-%m").strftime("%B %Y")


def build_wrapped(ym: str) -> bool:
    """Render the card for month `ym` (YYYY-MM). Returns True if written."""
    from PIL import Image, ImageDraw

    releases = json.loads(SITE_JSON.read_text(encoding="utf-8")).get("releases", [])
    month = [r for r in releases if (r.get("date") or "").startswith(ym)]
    if not month:
        print(f"wrapped: no releases in {ym} — skipping.")
        return False

    byco: dict[str, int] = {}
    for r in month:
        byco[r["company"]] = byco.get(r["company"], 0) + 1
    top_co, top_n = sorted(byco.items(), key=lambda x: -x[1])[0]
    open_p = round(sum(1 for r in month if r.get("open_source")) / len(month) * 100)
    bytype: dict[str, int] = {}
    for r in month:
        bytype[r["type"]] = bytype.get(r["type"], 0) + 1
    top_type = sorted(bytype.items(), key=lambda x: -x[1])[0][0]

    W, H = 1200, 630
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for y in range(H):  # subtle gradient
        f = y / H
        d.line([(0, y), (W, y)], fill=(11 + int(10 * f), 13 + int(8 * f), 23 + int(24 * f)))
    for r_ in (140, 230, 320):  # radar rings, top-right
        d.ellipse([W - 180 - r_, -60 - r_ // 3, W - 180 + r_, -60 + r_ // 3 + r_], outline=(34, 211, 238, 40), width=2)

    d.text((70, 56), "AI RELEASE RADAR", font=_font(30), fill=CYAN)
    d.text((70, 100), f"{_month_label(ym)} — Wrapped", font=_font(58), fill=WHITE)

    d.text((70, 230), str(len(month)), font=_font(120), fill=PURPLE)
    d.text((70, 360), "releases tracked", font=_font(28, bold=False), fill=MUTED)

    x2 = 480
    rows = [
        ("Busiest lab", f"{top_co} ({top_n})", CYAN),
        ("Open-source share", f"{open_p}%", GREEN),
        ("Top release type", top_type.upper(), PURPLE),
    ]
    y = 240
    for label, value, color in rows:
        d.text((x2, y), label.upper(), font=_font(20, bold=False), fill=MUTED)
        d.text((x2, y + 28), value, font=_font(44), fill=color)
        y += 110

    d.text((70, 560), "koha1312.github.io/ai-release-radar — auto-tracked, source-cited, no hype",
           font=_font(22, bold=False), fill=MUTED)

    WRAPPED_DIR.mkdir(parents=True, exist_ok=True)
    out = WRAPPED_DIR / f"{ym}.png"
    img.save(out)
    shutil.copyfile(out, WRAPPED_DIR / "latest.png")
    print(f"wrapped: wrote {out.name} ({len(month)} releases).")
    return True


def ensure_current() -> None:
    """Build last month's card if missing (idempotent; run from refresh)."""
    from datetime import timedelta

    now = datetime.now(timezone.utc)
    prev_ym = (datetime(now.year, now.month, 1) - timedelta(days=1)).strftime("%Y-%m")
    if not (WRAPPED_DIR / f"{prev_ym}.png").exists():
        build_wrapped(prev_ym)
