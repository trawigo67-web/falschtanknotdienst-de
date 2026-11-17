#!/usr/bin/env python3
"""Erzeugt die Logo-Dateien (SVG mit in Pfade umgewandelter Schrift) in logo/out/."""
import pathlib, json
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import uharfbuzz as hb

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "logo/out"; OUT.mkdir(parents=True, exist_ok=True)
cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
SRC = ROOT / "fonts-src/node_modules/@fontsource-variable/sofia-sans-condensed/files/sofia-sans-condensed-latin-wght-normal.woff2"

def static(wght):
    f = TTFont(SRC); f = instancer.instantiateVariableFont(f, {"wght": wght}); f.flavor = None
    p = OUT / ("_ssc-%d.ttf" % wght); f.save(p); return p

def outline(text, wght, size, x0, baseline, tracking=0.0):
    """Gibt (Pfad, Breite) für text zurück; Ursprung links auf der Grundlinie."""
    path = static(wght)
    font = TTFont(path); gs = font.getGlyphSet(); upm = font["head"].unitsPerEm; s = size / upm
    face = hb.Face(path.read_bytes()); hbf = hb.Font(face)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(hbf, buf, {"kern": True, "liga": False})
    order = font.getGlyphOrder(); x = 0.0; d = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        pen = SVGPathPen(gs, ntos=lambda v: ("%.2f" % v).rstrip("0").rstrip("."))
        tp = TransformPen(pen, (s, 0, 0, -s, x0 + (x + pos.x_offset) * s, baseline - pos.y_offset * s))
        gs[order[info.codepoint]].draw(tp); d.append(pen.getCommands())
        x += pos.x_advance + tracking * upm
    return " ".join(d), x * s

GLYPH = ('<g transform="translate(100 100) scale(.9) translate(-113 -125)">'
         '<path d="M139 50A64 64 0 0 1 87.8 166.9" fill="none" stroke="#FF8A1F" stroke-width="15" stroke-linecap="round"/>'
         '<path d="M98.4 144 53.6 155.8 83 191.6z" fill="#FF8A1F"/>'
         '<g transform="translate(-6 -9) rotate(-24 108 92)" fill="none" stroke="{c}" stroke-linecap="round" stroke-linejoin="round">'
         '<rect x="82" y="60" width="66" height="36" rx="11" fill="{c}" stroke="none"/><rect x="141" y="65" width="17" height="26" rx="6" fill="{c}" stroke="none"/>'
         '<rect x="75" y="66" width="13" height="24" rx="4" fill="{c}" stroke="none"/><path d="M84 78H65q-9 0-13 8l-7 13" stroke-width="15.5"/>'
         '<path d="M98 96v20a11 11 0 0 0 11 11h18a11 11 0 0 0 11-11V96" stroke-width="9.5"/></g></g>')
GRAD = '<linearGradient id="t" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#11636F"/><stop offset="1" stop-color="#06323B"/></linearGradient>'

def tile(rx=46, keyline=False, scale=1.0):
    g = GLYPH.format(c="#fff")
    if scale != 1.0: g = '<g transform="translate(100 100) scale(%s) translate(-100 -100)">%s</g>' % (scale, g)
    k = '<rect x="9" y="9" width="182" height="182" rx="%d" fill="none" stroke="#fff" stroke-width="4"/>' % max(rx - 8, 0) if keyline else ""
    return '<rect width="200" height="200" rx="%d" fill="url(#t)"/>%s%s' % (rx, k, g)

def svg(w, h, body, defs=GRAD):
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" width="%s" height="%s"><defs>%s</defs>%s</svg>\n' % (w, h, w, h, defs, body)

brand = cfg["brandHtml"]            # z. B. tank<b>ab</b>pumpen
import re
parts = [(m.group(2) or m.group(3), bool(m.group(2))) for m in re.finditer(r"(<b>(.*?)</b>)|([^<]+)", brand)]
tld = cfg["tld"]

def lockup(ink, accent, muted, tagline=None, tag_color=None):
    size = 168; base = 150; x = 248; body = '<g>%s</g>' % tile()
    for txt, hot in parts:
        d, w = outline(txt, 800, size, x, base, 0.004)
        body += '<path d="%s" fill="%s"/>' % (d, accent if hot else ink); x += w
    d, w = outline(tld, 700, size, x, base, 0.004); body += '<path d="%s" fill="%s"/>' % (d, muted); x += w
    return svg(round(x + 4), 200, body)

(OUT / "zeichen.svg").write_text(svg(200, 200, tile()), encoding="utf-8")
(OUT / "zeichen-schild.svg").write_text(svg(200, 200, tile(keyline=True, scale=.84)), encoding="utf-8")
(OUT / "profilbild.svg").write_text(svg(200, 200, tile(rx=0, scale=.82)), encoding="utf-8")
(OUT / "icon-vollflaeche.svg").write_text(svg(200, 200, tile(rx=0, scale=.9)), encoding="utf-8")
(OUT / "icon-maskable.svg").write_text(svg(200, 200, tile(rx=0, scale=.7)), encoding="utf-8")
(OUT / "zeichen-ohne-kachel.svg").write_text(svg(200, 200, GLYPH.format(c="#0B4650"), defs=""), encoding="utf-8")
(OUT / "logo-hell.svg").write_text(lockup("#0B2126", "#E36C00", "#48626A"), encoding="utf-8")
(OUT / "logo-dunkel.svg").write_text(lockup("#FFFFFF", "#FF8A1F", "#CDE2E3"), encoding="utf-8")
for p in OUT.glob("_ssc-*.ttf"): p.unlink()
print("ok", sorted(p.name for p in OUT.iterdir()))
