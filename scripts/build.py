"""Builds the profile SVGs in ../assets from the sources in ./src.

Fonts are subset and embedded as data URIs: an SVG shown through <img> cannot
fetch anything, so everything it needs travels inside the file.

    python3 -m venv .venv && .venv/bin/pip install fonttools brotli
    .venv/bin/python scripts/build.py
"""

import base64
import io
import pathlib

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT.parent / "assets"

# Palette from muratgurhan.com (oklch tokens converted to hex).
BG = "#0f0c0a"
SHADE = "#090706"
INK = "#f6f2e9"
INK_SOFT = "#d9d2c4"
AMBER = "#f0b44a"
BRONZE = "#b8742a"
MINT = "#5fd6b0"
TANGERINE = "#ff8a3d"

FIELDS = ["Deep Tech", "Marine", "Energy", "AI"]
WORK = ["Startups", "Scaleups", "Innovation", "R&D"]

GLYPHS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    " .,:;&/-·↗’'()"
)


def font_data(name: str, axes: dict[str, float]) -> str:
    # Pin the variable axes to the one instance we draw with; it halves the file.
    font = instancer.instantiateVariableFont(TTFont(SRC / name), axes)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    sub = subset.Subsetter(opts)
    sub.populate(text=GLYPHS)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def file_data(name: str, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode((SRC / name).read_bytes()).decode()


SERIF = font_data("fraunces-italic-latin.woff2", {"opsz": 72, "wght": 380})
SANS = font_data("schibsted-grotesk-normal-latin.woff2", {"wght": 500})

FONTS = f"""
@font-face {{ font-family: F; font-style: italic;
  src: url(data:font/woff2;base64,{SERIF}) format('woff2'); }}
@font-face {{ font-family: S;
  src: url(data:font/woff2;base64,{SANS}) format('woff2'); }}
.serif {{ font-family: F, Georgia, serif; font-style: italic; }}
.sans {{ font-family: S, 'Helvetica Neue', Arial, sans-serif; }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
"""

GRAIN = """
<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/>
  <feColorMatrix values="0 0 0 0 1  0 0 0 0 .95  0 0 0 0 .85  0 0 0 .55 0"/>
</filter>
"""


def interests(items: list[str], y: int, cx: int) -> str:
    parts = []
    for i, item in enumerate(items):
        if i:
            parts.append(f'<tspan fill="{AMBER}" dx="16">·</tspan><tspan dx="16">{item.replace("&", "&amp;")}</tspan>')
        else:
            parts.append(f"<tspan>{item.replace('&', '&amp;')}</tspan>")
    return (
        f'<text class="sans" x="{cx}" y="{y}" text-anchor="middle" font-size="21" '
        f'letter-spacing="2.6" fill="{INK_SOFT}">'
        + "".join(parts)
        + "</text>"
    )


def hero() -> str:
    w, h, cx = 1200, 460, 600
    # Slow amber light under dark water: blurred blobs drifting on long loops,
    # with thin ripple lines sliding across them.
    blobs = [
        (380, 300, 260, 90, AMBER, 0.55, "a", 26),
        (820, 330, 300, 80, BRONZE, 0.6, "b", 32),
        (600, 360, 380, 70, AMBER, 0.35, "c", 40),
        (180, 380, 220, 60, BRONZE, 0.4, "d", 36),
        (1040, 370, 220, 60, AMBER, 0.3, "e", 30),
    ]
    blob_svg = "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{c}" opacity="{o}" '
        f'style="animation: drift-{k} {t}s ease-in-out infinite alternate"/>'
        for x, y, rx, ry, c, o, k, t in blobs
    )
    drift = "".join(
        f"@keyframes drift-{k} {{ from {{ transform: translate(0,0) }} to {{ transform: translate({dx}px,{dy}px) }} }}"
        for k, dx, dy in [("a", 90, -18), ("b", -110, 12), ("c", 60, -10), ("d", 70, -14), ("e", -80, -8)]
    )
    ripples = "".join(
        f'<path d="M-200 {y} Q 100 {y - a} 400 {y} T 1000 {y} T 1600 {y}" fill="none" '
        f'stroke="{INK}" stroke-width="{sw}" opacity="{o}" '
        f'style="animation: slide {t}s linear infinite{" reverse" if r else ""}"/>'
        for y, a, sw, o, t, r in [
            (300, 6, 0.8, 0.10, 18, False),
            (326, 8, 1.0, 0.12, 24, True),
            (352, 5, 0.8, 0.09, 20, False),
            (380, 9, 1.2, 0.12, 28, True),
            (404, 6, 0.8, 0.08, 22, False),
            (430, 10, 1.2, 0.10, 30, True),
        ]
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Murat Gurhan. Entrepreneur. Deep Tech, Marine, Energy, AI. Startups, Scaleups, Innovation, R&amp;D.">
<style>{FONTS}
{drift}
@keyframes slide {{ from {{ transform: translateX(0) }} to {{ transform: translateX(-600px) }} }}
@keyframes breathe {{ 0%,100% {{ opacity: .9 }} 50% {{ opacity: 1 }} }}
.water {{ animation: breathe 9s ease-in-out infinite; }}
</style>
<defs>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="20"/></clipPath>
  <filter id="soft" x="-100%" y="-150%" width="300%" height="400%"><feGaussianBlur stdDeviation="55"/></filter>
  <linearGradient id="horizon" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BG}" stop-opacity="1"/>
    <stop offset=".45" stop-color="{BG}" stop-opacity=".55"/>
    <stop offset="1" stop-color="{BG}" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="veil" cx=".5" cy=".45" r=".75">
    <stop offset=".55" stop-color="{SHADE}" stop-opacity="0"/>
    <stop offset="1" stop-color="{SHADE}" stop-opacity=".85"/>
  </radialGradient>
  <linearGradient id="fade" x1="0" x2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset=".2" stop-color="#fff" stop-opacity="1"/>
    <stop offset=".8" stop-color="#fff" stop-opacity="1"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <mask id="edges"><rect width="{w}" height="{h}" fill="url(#fade)"/></mask>
  {GRAIN}
</defs>
<g clip-path="url(#frame)">
  <rect width="{w}" height="{h}" fill="{BG}"/>
  <g class="water" filter="url(#soft)">{blob_svg}</g>
  <g mask="url(#edges)">{ripples}</g>
  <rect width="{w}" height="{h * 0.7:.0f}" fill="url(#horizon)"/>
  <rect width="{w}" height="{h}" fill="url(#veil)"/>
  <rect width="{w}" height="{h}" filter="url(#grain)" opacity=".07"/>

  <text class="sans" x="{cx}" y="122" text-anchor="middle" font-size="18" font-weight="500"
        letter-spacing="6" fill="{AMBER}">ENTREPRENEUR</text>
  <text class="serif" x="{cx}" y="216" text-anchor="middle" font-size="92" font-weight="380"
        letter-spacing="-1" fill="{INK}">Murat Gurhan</text>
  {interests(FIELDS, 286, cx)}
  {interests(WORK, 326, cx)}
</g>
</svg>
"""


def venture(name: str, domain: str, logo: str, mime: str, logo_w: int, logo_h: int, glow: str, logo_x: int = 40) -> str:
    w, h = 600, 220
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{name}, {domain}">
<style>{FONTS}
@keyframes pulse {{ 0%,100% {{ opacity: .35; transform: translateX(0) }} 50% {{ opacity: .6; transform: translateX(-40px) }} }}
.glow {{ animation: pulse 12s ease-in-out infinite; }}
</style>
<defs>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="18"/></clipPath>
  <filter id="soft" x="-100%" y="-150%" width="300%" height="400%"><feGaussianBlur stdDeviation="45"/></filter>
  {GRAIN}
</defs>
<g clip-path="url(#frame)">
  <rect width="{w}" height="{h}" fill="{BG}"/>
  <ellipse class="glow" cx="520" cy="230" rx="200" ry="70" fill="{glow}" filter="url(#soft)"/>
  <rect width="{w}" height="{h}" filter="url(#grain)" opacity=".06"/>
  <text class="sans" x="40" y="58" font-size="17" font-weight="500" letter-spacing="4" fill="{INK_SOFT}">CURRENT VENTURE</text>
  <image href="{file_data(logo, mime)}" x="{logo_x}" y="{(h - logo_h) / 2 + 2:.0f}" width="{logo_w}" height="{logo_h}"/>
  <text class="sans" x="40" y="186" font-size="21" letter-spacing=".6" fill="{INK}">{domain} <tspan fill="{glow}">↗</tspan></text>
</g>
</svg>
"""


def button(label: str, accent: str) -> str:
    w, h = 220, 52
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">
<style>{FONTS}</style>
<rect width="{w}" height="{h}" rx="26" fill="{BG}"/>
<text class="sans" x="{w / 2}" y="32" text-anchor="middle" font-size="16" font-weight="500" letter-spacing="1.2" fill="{INK}">{label} <tspan fill="{accent}">↗</tspan></text>
</svg>
"""


OUT.mkdir(exist_ok=True)
(OUT / "hero.svg").write_text(hero())
# leanecocell.png is 1114×276; dojofood.svg is 520×150.
(OUT / "venture-lec.svg").write_text(
    venture("Lean Eco Cell", "leanecocell.com", "leanecocell.png", "image/png", 250, 62, MINT)
)
(OUT / "venture-dojofood.svg").write_text(
    venture("dojofood", "dojofood.com", "dojofood.svg", "image/svg+xml", 222, 64, TANGERINE, logo_x=17)
)
(OUT / "btn-site.svg").write_text(button("muratgurhan.com", AMBER))
(OUT / "btn-linkedin.svg").write_text(button("LinkedIn", AMBER))
for f in sorted(OUT.iterdir()):
    print(f"{f.name:24} {f.stat().st_size // 1024} KB")
