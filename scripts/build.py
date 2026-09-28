"""Build the profile panels as self-contained SVGs.

Real product screenshots and real brand logos are embedded as images, and the
Zensbot brand fonts (Outfit, JetBrains Mono) are embedded as subsets, so the
panels render the same on github.com as they do here.

Run: uv run --with fonttools --with pillow python scripts/build.py
"""
import base64
import io
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools import subset
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
SRC = ROOT / "src"
BRANDS = Path.home() / "Developer/repos/ads-factory/businesses"
FONTS = Path.home() / "Developer/repos/ads-factory/businesses/zensbot-course/assets/fonts"

INK, MUTED, LINE, PANEL, ACCENT = "#0E1116", "#5B6472", "#E3E6EB", "#F6F7F9", "#1765FD"
SANS, MONO = "Outfit", "JBMono"
W = 840


# ---------- assets ----------

def data_uri(img: Image.Image, fmt: str) -> str:
    buf = io.BytesIO()
    if fmt == "JPEG":
        img.convert("RGB").save(buf, "JPEG", quality=84, optimize=True, progressive=True)
        mime = "image/jpeg"
    else:
        img.save(buf, "PNG", optimize=True)
        mime = "image/png"
    return f"data:{mime};base64,{base64.b64encode(buf.getvalue()).decode()}"


def shot(name: str, box: tuple[int, int, int, int], w: int, h: int) -> str:
    """Crop a site screenshot and size it for 2x display."""
    img = Image.open(SRC / f"hi-{name}.png").crop(box)
    return data_uri(img.resize((w * 2, h * 2), Image.LANCZOS), "JPEG")


def logo(path: str, h: int) -> tuple[str, int]:
    """Trim a logo's empty margin and size it to a display height. Returns (uri, display width)."""
    img = Image.open(path if Path(path).is_absolute() else BRANDS / path).convert("RGBA")
    img = knock_out_white(trim(trim(img)))
    w = round(img.width * h / img.height)
    return data_uri(img.resize((w * 2, h * 2), Image.LANCZOS), "PNG"), w


def knock_out_white(img: Image.Image) -> Image.Image:
    """Some logo files sit on a solid white box. Make that box transparent, fading the edge."""
    if img.getpixel((0, 0))[3] < 250 or min(img.getpixel((0, 0))[:3]) < 240:
        return img
    rgb = img.convert("RGB")
    lightness = rgb.convert("L").point(lambda v: 0 if v >= 250 else 255 if v <= 200 else round((250 - v) * 5.1))
    out = img.copy()
    out.putalpha(lightness)
    return out


def trim(img: Image.Image) -> Image.Image:
    """Crop away transparent margin, then any solid margin matching the corner colour."""
    bbox = img.getchannel("A").point(lambda a: 255 if a > 10 else 0).getbbox()
    img = img.crop(bbox) if bbox else img
    corner = img.getpixel((0, 0))
    if corner[3] < 10:
        return img
    diff = Image.new("L", img.size)
    px, dp = img.load(), diff.load()
    for y in range(img.height):
        for x in range(img.width):
            p = px[x, y]
            if p[3] > 10 and sum(abs(p[i] - corner[i]) for i in range(3)) > 60:
                dp[x, y] = 255
    bbox = diff.getbbox()
    return img.crop(bbox) if bbox else img


def font_face(file: str, family: str, weight: int, text: str) -> str:
    opts = subset.Options()
    opts.layout_features = ["kern", "liga"]
    font = subset.load_font(str(FONTS / file), opts)
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return (f"@font-face{{font-family:{family};font-weight:{weight};"
            f"src:url(data:font/ttf;base64,{b64}) format('truetype');}}")


# ---------- svg primitives ----------

def text(x, y, s, size, weight=400, fill=INK, family=SANS, ls=0.0, anchor="start") -> str:
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" letter-spacing="{ls}" text-anchor="{anchor}">{escape(s)}</text>')


def lines(x, y, rows, size, step, fill=MUTED, weight=400) -> str:
    return "".join(text(x, y + i * step, r, size, weight, fill) for i, r in enumerate(rows))


def frame(uid, uri, x, y, w, h, r=10) -> str:
    """A real screenshot with rounded corners, a hairline edge and a soft tinted shadow."""
    return (f'<clipPath id="{uid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/></clipPath>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="#fff" filter="url(#sh)"/>'
            f'<image href="{uri}" x="{x}" y="{y}" width="{w}" height="{h}" clip-path="url(#{uid})" '
            f'preserveAspectRatio="xMidYMin slice"/>'
            f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="{r - .5}" fill="none" '
            f'stroke="#0E1116" stroke-opacity=".10"/>')


def img(uri, x, y, w, h) -> str:
    return f'<image href="{uri}" x="{x}" y="{y}" width="{w}" height="{h}"/>'


STYLE_MOTION = """
@media (prefers-reduced-motion: no-preference){
 .in{animation:rise 1s cubic-bezier(.16,1,.3,1) both}
 .d1{animation-delay:.08s}.d2{animation-delay:.2s}.d3{animation-delay:.34s}.d4{animation-delay:.48s}
 @keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
}"""


def svg(name, h, body, fonts, label) -> None:
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W if name != "half" else 414} {h}" '
           f'role="img" aria-label="{escape(label)}">'
           f"<style>{fonts}{STYLE_MOTION}</style>"
           '<defs><filter id="sh" x="-20%" y="-20%" width="140%" height="160%">'
           '<feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="#1B2B4B" flood-opacity=".14"/>'
           "</filter></defs>"
           f"{body}</svg>")
    (OUT / f"{name}.svg").write_text(doc)


def panel(w, h, clip_id="p") -> tuple[str, str]:
    """Rounded panel; returns (open, close) so content is clipped to it."""
    return (f'<clipPath id="{clip_id}"><rect width="{w}" height="{h}" rx="16"/></clipPath>'
            f'<g clip-path="url(#{clip_id})"><rect width="{w}" height="{h}" fill="{PANEL}"/>',
            f'</g><rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="15.5" fill="none" stroke="{LINE}"/>')


# ---------- panels ----------

COPY = dict(
    name="Hassan Arshad",
    hero=["I co-founded Zensbot. We build AI", "products used every day by schools,", "law firms and sales teams."],
    zl_head="The LMS 500+ institutes run on.",
    zl_body=["Web, mobile and desktop apps with live classes,", "all under each institute's own brand."],
    qa_head="AI legal research for Pakistan.",
    qa_body=["Every answer cites the judgment", "it came from."],
    cb_head="Sales meetings, booked by AI.",
    cb_body=["Finds your buyers, writes in your voice", "and puts the call on your calendar."],
    wall="Our products, and the companies we've built for",
)
EXTRA = ("AI agents behind every email 5 zensbot.com coldbot.pro qanoonai.pk zenslearn.com → 500+ 10,000+ institutes users 16.3M "
         "judgments across 21 jurisdictions Backed by PKR 14M in investment")
ALL_TEXT = " ".join(v if isinstance(v, str) else " ".join(v) for v in COPY.values()) + EXTRA


def fonts_css() -> str:
    return "".join([
        font_face("Outfit-Regular.ttf", SANS, 400, ALL_TEXT),
        font_face("Outfit-SemiBold.ttf", SANS, 600, ALL_TEXT),
        font_face("JetBrainsMono-Regular.ttf", MONO, 400, ALL_TEXT),
    ])


def hero(fc) -> None:
    h = 380
    zb, zbw = logo("zensbot/assets/logos/horizontal.png", 22)
    o, c = panel(W, h)
    body = o + (
        f'<g class="in d1">{img(zb, 44, 44, zbw, 22)}</g>'
        f'<g class="in d2">{text(42, 164, COPY["name"], 54, 600, INK, ls=-1.8)}'
        f'{lines(44, 206, COPY["hero"], 18, 27)}'
        f'{text(44, 318, "zensbot.com →", 14, 400, ACCENT, MONO)}</g>'
        f'<g class="in d2">{frame("f1", shot("qanoonai", (0, 0, 2880, 1800), 336, 210), 470, 34, 336, 210)}</g>'
        f'<g class="in d3">{frame("f2", shot("coldbot", (0, 0, 2880, 1800), 336, 210), 418, 112, 336, 210)}</g>'
        f'<g class="in d4">{frame("f3", shot("zenslearn", (0, 0, 2880, 1800), 336, 210), 486, 190, 336, 210)}</g>'
    ) + c
    svg("hero", h, body, fc, "Hassan Arshad, co-founder of Zensbot")


def zenslearn(fc) -> None:
    h = 330
    lg, lw = logo("lms/assets/logos/masters/lockup-horizontal-transparent.png", 24)
    o, c = panel(W, h)
    stats = (text(44, 246, "500+", 34, 600, INK, ls=-1) + text(44, 270, "institutes", 13, 400, MUTED, MONO)
             + text(170, 246, "10,000+", 34, 600, INK, ls=-1) + text(170, 270, "users", 13, 400, MUTED, MONO))
    body = o + (
        f'<g class="in d1">{img(lg, 44, 42, lw, 24)}'
        f'{text(42, 124, COPY["zl_head"], 28, 600, INK, ls=-.6)}'
        f'{lines(44, 156, COPY["zl_body"], 15.5, 23)}{stats}</g>'
        f'<g class="in d3">{frame("z1", shot("zenslearn", (240, 760, 2640, 2140), 400, 230), 440, 100, 400, 230)}</g>'
        f'{text(796, 60, "zenslearn.com →", 13, 400, ACCENT, MONO, anchor="end")}'
    ) + c
    svg("zenslearn", h, body, fc, "ZensLearn: 500+ institutes, 10,000+ users")


def half(name, logo_path, logo_h, head, body_rows, stat, shot_name, box, link, label, extra="") -> None:
    w, h = 414, 440
    lg, lw = logo(logo_path, logo_h)
    o, c = panel(w, h, f"p{name}")
    body = o + (
        f'<g class="in d1">{img(lg, 32, 36, lw, logo_h)}'
        f'{text(30, 112, head, 23, 600, INK, ls=-.5)}'
        f'{lines(32, 140, body_rows, 14.5, 21)}{stat}{extra}</g>'
        f'<g class="in d3">{frame(f"h{name}", shot(shot_name, box, 372, 196), 32, 248, 372, 196)}</g>'
    ) + c
    svg_half(name, h, body, label, link)


def svg_half(name, h, body, label, link) -> None:
    body += text(382, 54, link, 12.5, 400, ACCENT, MONO, anchor="end")
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 414 {h}" role="img" aria-label="{escape(label)}">'
           f"<style>{FC}{STYLE_MOTION}</style>"
           '<defs><filter id="sh" x="-20%" y="-20%" width="140%" height="160%">'
           '<feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="#1B2B4B" flood-opacity=".14"/>'
           "</filter></defs>"
           f"{body}</svg>")
    (OUT / f"{name}.svg").write_text(doc)


def formixx_mark(h: int) -> tuple[str, int]:
    """Formixx ships only as a wordmark on a black tile. Keep the lettering, recoloured to ink."""
    src = Image.open(BRANDS.parent / "video-engine/public/images/formixx/logo-on-black.png").convert("RGBA")
    grey = Image.new("RGB", src.size, "white")
    grey.paste(src, mask=src.getchannel("A"))
    grey = grey.convert("L")
    tile = grey.point(lambda v: 255 if v < 60 else 0).getbbox()
    ix, iy = (tile[2] - tile[0]) // 10, (tile[3] - tile[1]) // 10
    inner = grey.crop((tile[0] + ix, tile[1] + iy, tile[2] - ix, tile[3] - iy))
    ink = inner.point(lambda v: 255 if v > 140 else 0)
    ink = ink.crop(ink.getbbox())
    mark = Image.new("RGBA", ink.size, INK)
    mark.putalpha(ink)
    w = round(mark.width * h / mark.height)
    return data_uri(mark.resize((w * 2, h * 2), Image.LANCZOS), "PNG"), w


def wall(fc) -> None:
    h = 150
    items = [
        ("zensbot/assets/logos/horizontal.png", 24),
        ("coldbot/assets/logos/transparent/lockup-horizontal.png", 24),
        ("qanoonai/assets/logos/qanoonai-lockup-horizontal-dark.png", 30),
        ("lms/assets/logos/masters/lockup-horizontal-transparent.png", 22),
        ("ict/assets/logos/ict-logo.png", 34),
    ]
    logos = [(*logo(p, lh), lh) for p, lh in items]
    logos.insert(4, (*formixx_mark(24), 24))
    gap = (W - 88 - sum(lw for _, lw, _ in logos)) / (len(logos) - 1)
    x, row = 44.0, []
    for i, (uri, lw, lh) in enumerate(logos):
        row.append(f'<g class="in d{min(4, 1 + i // 2)}">{img(uri, round(x), round(96 - lh / 2), lw, lh)}</g>')
        x += lw + gap
    o, c = panel(W, h)
    body = o + text(44, 46, COPY["wall"], 15, 400, MUTED) + "".join(row) + c
    svg("logos", h, body, fc, "Zensbot, ColdBot, QanoonAI, ZensLearn, Formixx, ICT")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    FC = fonts_css()
    hero(FC)
    zenslearn(FC)
    half("qanoonai", "qanoonai/assets/logos/qanoonai-lockup-horizontal-dark.png", 30,
         COPY["qa_head"], COPY["qa_body"],
         text(32, 206, "16.3M", 30, 600, INK, ls=-1) + text(124, 200, "judgments across", 12, 400, MUTED, MONO)
         + text(124, 216, "21 jurisdictions", 12, 400, MUTED, MONO),
         "qanoonai", (360, 120, 2520, 1500), "qanoonai.pk →", "QanoonAI: 16.3M judgments across 21 jurisdictions")
    half("coldbot", "coldbot/assets/logos/transparent/lockup-horizontal.png", 26,
         COPY["cb_head"], COPY["cb_body"],
         text(32, 206, "5", 30, 600, INK) + text(62, 200, "AI agents behind", 12, 400, MUTED, MONO)
         + text(62, 216, "every email", 12, 400, MUTED, MONO),
         "coldbot", (360, 120, 2520, 1500), "coldbot.pro →", "ColdBot: sales meetings, booked by AI")
    wall(FC)
    for p in sorted(OUT.glob("*.svg")):
        print(f"{p.stat().st_size // 1024:>5} KB  {p.name}")
