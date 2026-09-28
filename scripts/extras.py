"""Contact buttons and the moving strip of client logos."""
import math
import re
from pathlib import Path

from build import (ACCENT, INK, LINE, MONO, MUTED, OUT, PANEL, SANS, SRC, W, COPY, logo, text)

REPOS = Path.home() / "Developer/repos"
SITE = REPOS / "zensbot/public/clients"

# Case-study clients first, then the other delivered work, then the brokerages.
# Order follows zensbot.com (lib/proof/clients.ts); a new client is added there first.
ROW_A = [
    Path.home() / "Developer/repos/ads-factory/businesses/qanoonai/assets/logos/qanoonai-lockup-horizontal-dark.png", SITE / "ict.png", REPOS / "Atlas_Eng_Website/public/images/global/logo.png",
    SITE / "penguin-swim.png", SITE / "tsfa-creative.png", REPOS / "MATHLLC LANDING PAGE/assets/brand/math-logo@2x.png",
    SITE / "pak-health.png", SITE / "medcare.png", SITE / "dayemens.png", SITE / "printeazy.png",
]
ROW_B = [SITE / f"real-estate/{n}.png" for n in (
    "crestline-realty", "copper-oak-homes", "blue-mesa-real-estate", "bright-harbor-realty",
    "pioneer-peak-realty", "urban-nest-realty", "golden-mesa-realty", "maple-crown-realty",
    "summit-lane-homes", "desert-key-homes", "north-ridge-real-estate", "valleynest-realty",
    "horizon-peak-realty", "willow-stone-homes", "sunridge-real-estate", "saguaro-living",
)]

CONTACTS = [
    ("linkedin", "LinkedIn", "in/hassanarshadd", "linkedin.svg"),
    ("instagram", "Instagram", "@zensbot", "instagram.svg"),
    ("email", "Email", "hassan@zensbot.com", "envelope.svg"),
]


def icon(file: str, x: float, y: float, size: float) -> str:
    """Place a library glyph (Simple Icons / Phosphor), scaled from its own viewBox."""
    raw = (SRC / file).read_text()
    vb = float(re.search(r'viewBox="0 0 ([\d.]+)', raw).group(1))
    paths = "".join(re.findall(r"<path[^>]*/>", raw))
    return f'<g transform="translate({x} {y}) scale({size / vb})" fill="{INK}">{paths}</g>'


def doc(w: int, h: int, fc: str, css: str, body: str, label: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">'
            f"<style>{fc}{css}</style>{body}</svg>")


def contact_buttons(fc: str) -> None:
    w, h = 274, 76
    for slug, label, handle, glyph in CONTACTS:
        body = (
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="15.5" fill="{PANEL}" stroke="{LINE}"/>'
            f'<rect x="18" y="18" width="40" height="40" rx="10" fill="#fff" stroke="{LINE}"/>'
            + icon(glyph, 28, 28, 20)
            + text(72, 35, label, 16, 600, INK)
            + text(72, 55, handle, 12, 400, MUTED, MONO)
            + text(w - 20, 44, "↗", 16, 400, ACCENT, anchor="end")
        )
        (OUT / f"contact-{slug}.svg").write_text(doc(w, h, fc, "", body, f"{label}: {handle}"))


def sized(path: Path) -> tuple[str, int, int]:
    """Give every mark roughly the same visual weight, whatever its shape."""
    probe_uri, probe_w = logo(str(path), 100)
    aspect = probe_w / 100
    lh = max(24, min(46, round(math.sqrt(3400 / aspect))))
    uri, lw = logo(str(path), lh)
    return uri, lw, lh


def row(paths: list[Path], y: float, gap: int) -> tuple[str, int]:
    items, x = [], 0
    for p in paths:
        uri, lw, lh = sized(p)
        items.append(f'<image href="{uri}" x="{x}" y="{round(y - lh / 2)}" width="{lw}" height="{lh}"/>')
        x += lw + gap
    return "".join(items), x


def clients(fc: str) -> None:
    h, gap = 230, 60
    a, wa = row(ROW_A, 0, gap)
    b, wb = row(ROW_B, 0, gap)
    speed = 34  # px per second: slow enough to read each name
    css = f"""
@media (prefers-reduced-motion: no-preference){{
 .ra{{animation:ra {wa / speed:.0f}s linear infinite}}
 .rb{{animation:rb {wb / speed:.0f}s linear infinite}}
 @keyframes ra{{from{{transform:translateX(0)}}to{{transform:translateX(-{wa}px)}}}}
 @keyframes rb{{from{{transform:translateX(-{wb}px)}}to{{transform:translateX(0)}}}}
}}"""
    body = (
        '<defs><linearGradient id="fade" x1="0" x2="1">'
        '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".08" stop-color="#fff"/>'
        '<stop offset=".92" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        f'<mask id="m"><rect width="{W}" height="{h}" fill="url(#fade)"/></mask>'
        f'<clipPath id="p"><rect width="{W}" height="{h}" rx="16"/></clipPath></defs>'
        f'<g clip-path="url(#p)"><rect width="{W}" height="{h}" fill="{PANEL}"/>'
        + text(44, 52, COPY["wall"], 20, 600, INK, SANS, ls=-.3)
        + f'<g mask="url(#m)">'
        f'<defs><g id="la">{a}</g><g id="lb">{b}</g></defs>'
        f'<g transform="translate(0 116)"><g class="ra"><use href="#la"/><use href="#la" x="{wa}"/></g></g>'
        f'<g transform="translate(0 184)"><g class="rb"><use href="#lb"/><use href="#lb" x="{wb}"/></g></g>'
        "</g></g>"
        f'<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="15.5" fill="none" stroke="{LINE}"/>'
    )
    names = ", ".join(p.stem.replace("-", " ").replace("@2x", "") for p in ROW_A + ROW_B)
    (OUT / "clients.svg").write_text(doc(W, h, fc, css, body, f"{COPY['wall']}: {names}"))


def build(fc: str) -> None:
    for old in ("logos.svg",):
        (OUT / old).unlink(missing_ok=True)
    contact_buttons(fc)
    clients(fc)
