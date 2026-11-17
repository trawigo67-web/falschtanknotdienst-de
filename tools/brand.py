#!/usr/bin/env python3
"""Logo-Schriftzüge, Vorschaubild (og.png) und Übersicht für jede Website. Aufruf: brand.py sites/a.json sites/b.json"""
import pathlib, json, re, sys, asyncio
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import uharfbuzz as hb
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "fonts-src/node_modules/@fontsource-variable/sofia-sans-condensed/files/sofia-sans-condensed-latin-wght-normal.woff2"
TMP = ROOT / "logo/_tmp"; TMP.mkdir(parents=True, exist_ok=True)
_static = {}
def static(wght):
    if wght not in _static:
        f = instancer.instantiateVariableFont(TTFont(SRC), {"wght": wght}); f.flavor = None
        p = TMP / ("ssc-%d.ttf" % wght); f.save(p); _static[wght] = p
    return _static[wght]

def outline(text, wght, size, x0, baseline, tracking=0.004):
    path = static(wght); font = TTFont(path); gs = font.getGlyphSet(); upm = font["head"].unitsPerEm; s = size / upm
    hbf = hb.Font(hb.Face(path.read_bytes())); buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(hbf, buf, {"kern": True, "liga": False})
    order = font.getGlyphOrder(); x = 0.0; d = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        pen = SVGPathPen(gs, ntos=lambda v: ("%.2f" % v).rstrip("0").rstrip("."))
        gs[order[info.codepoint]].draw(TransformPen(pen, (s, 0, 0, -s, x0 + (x + pos.x_offset) * s, baseline - pos.y_offset * s)))
        d.append(pen.getCommands()); x += pos.x_advance + tracking * upm
    return " ".join(d), x * s

GLYPH = ('<g transform="translate(100 100) scale(.9) translate(-113 -125)">'
         '<path d="M139 50A64 64 0 0 1 87.8 166.9" fill="none" stroke="#FF8A1F" stroke-width="15" stroke-linecap="round"/>'
         '<path d="M98.4 144 53.6 155.8 83 191.6z" fill="#FF8A1F"/>'
         '<g transform="translate(-6 -9) rotate(-24 108 92)" fill="none" stroke="{c}" stroke-linecap="round" stroke-linejoin="round">'
         '<rect x="82" y="60" width="66" height="36" rx="11" fill="{c}" stroke="none"/><rect x="141" y="65" width="17" height="26" rx="6" fill="{c}" stroke="none"/>'
         '<rect x="75" y="66" width="13" height="24" rx="4" fill="{c}" stroke="none"/><path d="M84 78H65q-9 0-13 8l-7 13" stroke-width="15.5"/>'
         '<path d="M98 96v20a11 11 0 0 0 11 11h18a11 11 0 0 0 11-11V96" stroke-width="9.5"/></g></g>')
GRAD = '<linearGradient id="t" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#11636F"/><stop offset="1" stop-color="#06323B"/></linearGradient>'
TILE = '<rect width="200" height="200" rx="46" fill="url(#t)"/>' + GLYPH.format(c="#fff")
def svg(w, h, body, defs=GRAD):
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" width="%s" height="%s"><defs>%s</defs>%s</svg>\n' % (w, h, w, h, defs, body)

def lockup(cfg, ink, accent, muted):
    parts = [(m.group(2) or m.group(3), bool(m.group(2))) for m in re.finditer(r"(<b>(.*?)</b>)|([^<]+)", cfg["brandHtml"])]
    size = 168; base = 150; x = 248; body = '<g>%s</g>' % TILE
    for txt, hot in parts:
        d, w = outline(txt, 800, size, x, base); body += '<path d="%s" fill="%s"/>' % (d, accent if hot else ink); x += w
    d, w = outline(cfg["tld"], 700, size, x, base); body += '<path d="%s" fill="%s"/>' % (d, muted); x += w
    return svg(round(x + 4), 200, body)

OG = '''<!DOCTYPE html><html><head><meta charset="utf-8"><style>
@font-face{font-family:"SSC";src:url("file://%(root)s/assets/fonts/ssc-latin.woff2") format("woff2");font-weight:600 900}
@font-face{font-family:"SS";src:url("file://%(root)s/assets/fonts/ss-latin.woff2") format("woff2");font-weight:400 700}
*{box-sizing:border-box}body{margin:0;width:1200px;height:630px;background:#0B4650;color:#fff;position:relative;overflow:hidden;font-family:SS}
.key{position:absolute;inset:18px;border:5px solid rgba(255,255,255,.93);border-radius:34px}
.in{position:absolute;inset:0;padding:70px 84px}
.logo{height:80px;display:block}
h1{font:800 114px/.95 SSC;margin:62px 0 28px;letter-spacing:-.6px}
p{font:400 40px/1.25 SS;color:#CDE2E3;margin:0;max-width:760px}
.g{position:absolute;right:34px;bottom:26px;width:320px;height:320px}
</style></head><body><div class="key"></div>
<svg class="g" viewBox="0 0 200 200">%(glyph)s</svg>
<div class="in"><img class="logo" src="file://%(lock)s" alt=""><h1>Falsch getankt?<br>Motor aus lassen.</h1><p>Wir pumpen den Tank direkt vor Ort ab. Rund um die Uhr.</p></div></body></html>'''

SHEET = '''<!DOCTYPE html><html lang="de"><head><meta charset="utf-8"><style>
@font-face{font-family:"SSC";src:url("file://%(root)s/assets/fonts/ssc-latin.woff2") format("woff2");font-weight:600 900}
@font-face{font-family:"SS";src:url("file://%(root)s/assets/fonts/ss-latin.woff2") format("woff2");font-weight:400 700}
*{box-sizing:border-box}body{margin:0;width:1600px;background:#EEF3F2;color:#0B2126;font:400 22px/1.45 SS;padding:52px 60px 48px}
h1{font:800 52px/1 SSC;margin:0 0 10px}.sub{font-size:23px;color:#48626A;margin:0 0 34px;max-width:1200px}
.grid{display:grid;grid-template-columns:300px 1fr;gap:26px 44px;align-items:start}
.mark{width:300px;height:300px;display:block}.cap{font:600 17px/1.3 SS;color:#48626A;margin-top:12px}
.col{display:grid;gap:18px}
.panel{border-radius:20px;padding:26px 34px;display:flex;align-items:center}
.light{background:#fff;border:1.5px solid #D2DDDB}.dark{background:#0B4650}
.panel img{height:78px;display:block;max-width:100%%}
.lbl{font:700 19px SS;color:#48626A;margin:14px 0 -4px}
</style></head><body>
<h1>Das Logo für beide Adressen</h1>
<p class="sub">Dasselbe Bildzeichen, zwei Schriftzüge. Die Zapfpistole dreht um: Der Schlauch wird zum Rückpfeil, der falsche Kraftstoff kommt wieder heraus.</p>
<div class="grid"><div><img class="mark" src="file://%(root)s/logo/out/zeichen.svg" alt=""><div class="cap">Bildzeichen für beide Seiten, App-Symbol, Profilbild und Fahrzeug</div></div>
<div class="col">%(rows)s</div></div></body></html>'''

async def main(paths):
    cfgs = [dict(json.loads((ROOT / "config.json").read_text(encoding="utf-8")), **json.loads(pathlib.Path(p).read_text(encoding="utf-8"))) for p in paths]
    rows = ""
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--allow-file-access-from-files"])
        for cfg in cfgs:
            name = cfg["brand"]; d = ROOT / "logo/final" / name; d.mkdir(parents=True, exist_ok=True)
            hell = d / ("logo-%s-hell.svg" % name); dunkel = d / ("logo-%s-dunkel.svg" % name)
            hell.write_text(lockup(cfg, "#0B2126", "#E36C00", "#48626A"), encoding="utf-8")
            dunkel.write_text(lockup(cfg, "#FFFFFF", "#FF8A1F", "#CDE2E3"), encoding="utf-8")
            for f in (hell, dunkel):
                src = f.read_text(encoding="utf-8"); vw, vh = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', src).groups()); w = 2400; h = round(w * vh / vw)
                pg = await b.new_page(viewport={"width": w, "height": h})
                await pg.set_content('<html><body style="margin:0;background:transparent">%s</body></html>' % src.replace('<svg ', '<svg style="display:block;width:%dpx;height:%dpx" ' % (w, h), 1))
                await pg.screenshot(path=str(f.with_suffix(".png")), omit_background=True); await pg.close()
            og = TMP / ("og-%s.html" % name); og.write_text(OG % {"root": ROOT, "lock": dunkel, "glyph": GLYPH.format(c="#fff")}, encoding="utf-8")
            pg = await b.new_page(viewport={"width": 1200, "height": 630}); await pg.goto("file://%s" % og); await pg.wait_for_timeout(400)
            await pg.screenshot(path=str(ROOT / "out" / cfg["domain"] / "og.png")); await pg.close()
            rows += '<div class="lbl">%s</div><div class="panel light"><img src="file://%s" alt=""></div><div class="panel dark"><img src="file://%s" alt=""></div>' % (cfg["domain"], hell, dunkel)
        sheet = TMP / "sheet.html"; sheet.write_text(SHEET % {"root": ROOT, "rows": rows}, encoding="utf-8")
        pg = await b.new_page(viewport={"width": 1600, "height": 900}); await pg.goto("file://%s" % sheet); await pg.wait_for_timeout(400)
        await pg.screenshot(path=str(ROOT / "logo/final/logo-uebersicht-beide-adressen.png"), full_page=True); await pg.close()
        await b.close()
    print("ok", sorted(str(p.relative_to(ROOT)) for p in (ROOT / "logo/final").rglob("*") if p.is_file()))

asyncio.run(main(sys.argv[1:]))
