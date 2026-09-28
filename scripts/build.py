"""Generate the product cards, client marquee and stack strip as animated SVGs."""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent.parent / "assets"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
W, H = 410, 250


def counter(frames: list[str], x: int, y: int, color: str) -> str:
    """Number that counts up once on load, then holds. Without animation it shows the final value."""
    n, dur, parts = len(frames), 2.2, []
    for i, label in enumerate(frames):
        # frame i shows during [ (i+1)/(n+1), (i+2)/(n+1) ); the first slot is a short pause on frame 0
        slots = [0] * (n + 1)
        slots[i + 1] = 1
        if i == 0:
            slots[0] = 1
        vals = ";".join(map(str, slots)) + (";1" if i == n - 1 else ";0")
        keys = ";".join(f"{j / (n + 1):.3f}" for j in range(n + 1)) + ";1"
        base = "1" if i == n - 1 else "0"
        parts.append(
            f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="46" font-weight="800" '
            f'letter-spacing="-1.5" fill="{color}" opacity="{base}">{escape(label)}'
            f'<animate attributeName="opacity" dur="{dur}s" begin="0s" fill="freeze" '
            f'calcMode="discrete" values="{vals}" keyTimes="{keys}"/></text>'
        )
    return "\n".join(parts)


def steps(labels: list[str], y: int, color: str) -> str:
    """Pipeline chips that light up one after another, on a loop."""
    n, x, out = len(labels), 28, []
    period = 1.1 * n + 1.5
    for i, label in enumerate(labels):
        w = 14 + 7.6 * len(label)
        t0, t1 = (1.1 * i) / period, (1.1 * i + 0.9) / period
        out.append(
            f'<g><rect x="{x}" y="{y}" width="{w:.0f}" height="26" rx="13" fill="{color}" '
            f'fill-opacity="0.08" stroke="{color}" stroke-opacity="0.35">'
            f'<animate attributeName="fill-opacity" dur="{period:.1f}s" repeatCount="indefinite" '
            f'values="0.08;0.08;0.55;0.08;0.08" keyTimes="0;{t0:.3f};{(t0 + t1) / 2:.3f};{t1:.3f};1"/></rect>'
            f'<text x="{x + w / 2:.0f}" y="{y + 17}" text-anchor="middle" font-family="{MONO}" '
            f'font-size="12" fill="#E2E8F0">{escape(label)}</text></g>'
        )
        x += w + 18
        if i < n - 1:
            out.append(f'<text x="{x - 13:.0f}" y="{y + 17}" font-family="{MONO}" font-size="12" fill="#475569">›</text>')
    return "\n".join(out)


def chips(labels: list[str], y: int, color: str) -> str:
    x, out = 28, []
    for label in labels:
        w = 16 + 7.4 * len(label)
        out.append(
            f'<rect x="{x}" y="{y}" width="{w:.0f}" height="24" rx="6" fill="#fff" fill-opacity="0.04" '
            f'stroke="#fff" stroke-opacity="0.08"/><text x="{x + 8}" y="{y + 16}" font-family="{MONO}" '
            f'font-size="12" fill="{color}">{escape(label)}</text>'
        )
        x += w + 8
    return "\n".join(out)


def card(slug, index, name, accent, lines, body, link, badge="LIVE"):
    tagline = "\n".join(
        f'<text x="28" y="{104 + 20 * i}" font-family="{SANS}" font-size="14.5" fill="#94A3B8">{escape(t)}</text>'
        for i, t in enumerate(lines)
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(name)}: {escape(' '.join(lines))}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0B0E17"/><stop offset="1" stop-color="#111626"/></linearGradient>
  <radialGradient id="glow" cx="1" cy="0" r="1"><stop offset="0" stop-color="{accent}" stop-opacity="0.28"/><stop offset="0.6" stop-color="{accent}" stop-opacity="0"/></radialGradient>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#glow)"><animate attributeName="opacity" dur="5s" repeatCount="indefinite" values="0.7;1;0.7"/></rect>
  <rect width="{W}" height="3" fill="{accent}"/>
  <text x="28" y="40" font-family="{MONO}" font-size="11" letter-spacing="2" fill="#64748B">{index}</text>
  <g transform="translate({W - 28} 30)">
    <rect x="{-(30 + 7.3 * len(badge)):.0f}" y="-2" width="{30 + 7.3 * len(badge):.0f}" height="20" rx="10" fill="{accent}" fill-opacity="0.12"/>
    <circle cx="{-(19 + 7.3 * len(badge)):.0f}" cy="8" r="3.5" fill="{accent}"><animate attributeName="opacity" dur="1.6s" repeatCount="indefinite" values="1;0.2;1"/></circle>
    <text x="-10" y="12" text-anchor="end" font-family="{MONO}" font-size="10.5" letter-spacing="1" fill="{accent}">{badge}</text>
  </g>
  <text x="26" y="78" font-family="{SANS}" font-size="30" font-weight="800" letter-spacing="-0.8" fill="#F8FAFC">{escape(name)}</text>
  {tagline}
  {body}
  <text x="28" y="{H - 20}" font-family="{MONO}" font-size="12" fill="{accent}">→ {escape(link)}</text>
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="17.5" fill="none" stroke="#fff" stroke-opacity="0.09"/>
</svg>'''
    (OUT / f"{slug}.svg").write_text(svg)


def stat_label(text: str, x: int, y: int) -> str:
    return f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="13" fill="#CBD5E1">{escape(text)}</text>'


card(
    "coldbot", "01 / SALES", "ColdBot", "#22D3EE",
    ["Finds the right buyers, writes emails that", "don't sound like AI, and books the meetings."],
    steps(["Find", "Verify", "Write", "Send", "Book"], 160, "#22D3EE"),
    "coldbot.pro",
)
card(
    "qanoonai", "02 / LEGAL", "QanoonAI", "#F59E0B",
    ["Pakistan's first AI legal intelligence platform,", "for citizens, lawyers and judges."],
    counter(["0", "2.4M", "6.1M", "9.8M", "13.2M", "16.3M"], 28, 192, "#FCD34D")
    + stat_label("court judgments", 186, 176)
    + stat_label("21 jurisdictions", 186, 194),
    "qanoonai.pk", badge="FUNDED",
)
card(
    "zenslearn", "03 / EDUCATION", "ZensLearn", "#34D399",
    ["White-label LMS: web, mobile, desktop and", "live classes, under the institute's brand."],
    counter(["0", "120+", "260+", "390+", "500+"], 28, 192, "#6EE7B7")
    + stat_label("institutes", 186, 176)
    + stat_label("10,000+ users", 186, 194),
    "zenslearn.com",
)
card(
    "opensource", "04 / OPEN SOURCE", "Built in public", "#A78BFA",
    ["Tools we use ourselves, free for anyone.", "Fork them, ship them, send a pull request."],
    chips(["ZensLoom · Rust", "ICT LMS · Vue", "DeerFlow · Py"], 160, "#C4B5FD"),
    "github.com/hassanarshad123", badge="MIT",
)


def marquee() -> None:
    """Clients we've built for, scrolling in a seamless loop."""
    clients = ["Formixx", "ICT Pakistan", "Atlas Engineering", "MATH LLC", "Penguin Swim School",
               "PrintEazy", "TSFA Creative", "Happyness365", "Dayemens"]
    # One text run, forced to an exact length, so the copy can sit flush behind it.
    spans = "".join(
        f'<tspan fill="#E2E8F0" fill-opacity="0.85">{escape(c)}</tspan>'
        f'<tspan fill="#6366F1" font-size="16" dx="0">\u2003\u2003\u2726\u2003\u2003</tspan>'
        for c in clients
    )
    loop = int(sum(11.2 * len(c) + 100 for c in clients))
    run = (f'<text y="0" font-family="{SANS}" font-size="20" font-weight="700" '
           f'textLength="{loop}" lengthAdjust="spacing" xml:space="preserve">{spans}</text>')
    row = run.replace('<text y', '<text x="0" y', 1)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 130" width="840" height="130" role="img" aria-label="Clients: {escape(', '.join(clients))}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0B0E17"/><stop offset="1" stop-color="#111626"/></linearGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.12" stop-color="#fff"/>
    <stop offset="0.88" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <mask id="m"><rect width="840" height="130" fill="url(#fade)"/></mask>
  <clipPath id="c"><rect width="840" height="130" rx="18"/></clipPath>
</defs>
<g clip-path="url(#c)">
  <rect width="840" height="130" fill="url(#bg)"/>
  <text x="420" y="36" text-anchor="middle" font-family="{MONO}" font-size="11" letter-spacing="3" fill="#64748B">ZENSBOT HAS SHIPPED FOR</text>
  <g mask="url(#m)"><g transform="translate(0 86)"><g>
    <animateTransform attributeName="transform" type="translate" from="0 0" to="{-loop:.0f} 0" dur="{loop / 45:.0f}s" repeatCount="indefinite"/>
    {row}
    <g transform="translate({loop:.0f} 0)">{row}</g>
  </g></g></g>
</g>
<rect x="0.5" y="0.5" width="839" height="129" rx="17.5" fill="none" stroke="#fff" stroke-opacity="0.09"/>
</svg>'''
    (OUT / "clients.svg").write_text(svg)


def stack() -> None:
    groups = [
        ("AI", "#A78BFA", ["OpenAI", "Claude", "RAG", "Agents"]),
        ("Backend", "#22D3EE", ["Python", "FastAPI", "Rust", "Celery"]),
        ("Frontend", "#34D399", ["Next.js", "TypeScript", "Flutter", "Electron"]),
        ("Infra", "#F59E0B", ["AWS", "Terraform", "Postgres", "Vercel"]),
    ]
    col_w, out = 840 / 4, []
    for gi, (title, color, items) in enumerate(groups):
        x0 = gi * col_w + 24
        out.append(f'<text x="{x0:.0f}" y="40" font-family="{MONO}" font-size="11" letter-spacing="2.5" fill="{color}">{title.upper()}</text>')
        for ii, item in enumerate(items):
            y = 70 + ii * 30
            delay = gi * 0.25 + ii * 0.12
            out.append(
                f'<g><animate attributeName="opacity" begin="0s" dur="{delay + 0.5:.2f}s" fill="freeze" values="0;0;1" keyTimes="0;{delay / (delay + 0.5):.3f};1"/>'
                f'<rect x="{x0:.0f}" y="{y - 15}" width="3" height="18" rx="1.5" fill="{color}"/>'
                f'<text x="{x0 + 12:.0f}" y="{y}" font-family="{SANS}" font-size="15" font-weight="600" fill="#E2E8F0">{escape(item)}</text></g>'
            )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 200" width="840" height="200" role="img" aria-label="Tech stack">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0B0E17"/><stop offset="1" stop-color="#111626"/></linearGradient>
  <clipPath id="c"><rect width="840" height="200" rx="18"/></clipPath>
</defs>
<g clip-path="url(#c)"><rect width="840" height="200" fill="url(#bg)"/>
{chr(10).join(out)}
</g>
<rect x="0.5" y="0.5" width="839" height="199" rx="17.5" fill="none" stroke="#fff" stroke-opacity="0.09"/>
</svg>'''
    (OUT / "stack.svg").write_text(svg)


marquee()
stack()
print(sorted(p.name for p in OUT.iterdir()))
