#!/usr/bin/env python3
"""Markenmaterial für jede Website: Logo-Dateien, App-Symbole und Teilen-Bild (og.png).

   python3 tools/brand.py                      alle Websites aus sites/*.json
   python3 tools/brand.py sites/tankdoktor.json   nur diese

   Ergebnis:
   - assets/brand/<name>/<thema>/icon.svg, icon-96.png (Browser-Tab), icon-180.png, icon-192.png, icon-512.png (App-Symbole), og.png (Teilen-Bild)
   - logo/<name>/...  Logo-Dateien als SVG (Schrift in Pfade umgewandelt) und PNG, im Farbthema "logoTheme" der Website
   Braucht: fontTools, uharfbuzz, playwright mit Chrome sowie die Schriftquellen unter fonts-src/ (npm-Pakete @fontsource-variable/sofia-sans und -condensed)."""
import pathlib, json, re, sys, asyncio, html as htmlmod
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import uharfbuzz as hb
from playwright.async_api import async_playwright
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import marks

ROOT = pathlib.Path(__file__).resolve().parent.parent
FS = ROOT / "fonts-src/node_modules/@fontsource-variable"
FONTS = {"ssc": FS / "sofia-sans-condensed/files/sofia-sans-condensed-latin-wght-normal.woff2",
         "ss": FS / "sofia-sans/files/sofia-sans-latin-wght-normal.woff2"}
TMP = ROOT / "logo/_tmp"; TMP.mkdir(parents=True, exist_ok=True)
THEMES = json.loads((ROOT / "src/themes.json").read_text(encoding="utf-8"))
_static = {}


def static(fam, wght):
    if (fam, wght) not in _static:
        TMP.mkdir(parents=True, exist_ok=True)
        f = instancer.instantiateVariableFont(TTFont(FONTS[fam]), {"wght": wght}); f.flavor = None
        p = TMP / ("%s-%d.ttf" % (fam, wght)); f.save(p); _static[(fam, wght)] = p
    return _static[(fam, wght)]


def outline(text, fam, wght, size, x0, baseline, tracking=0.004):
    """Text als Pfad. Rückgabe: (Pfad, Breite)."""
    path = static(fam, wght); font = TTFont(path); gs = font.getGlyphSet(); upm = font["head"].unitsPerEm; s = size / upm
    hbf = hb.Font(hb.Face(path.read_bytes())); buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(hbf, buf, {"kern": True, "liga": False})
    order = font.getGlyphOrder(); x = 0.0; d = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        pen = SVGPathPen(gs, ntos=lambda v: ("%.2f" % v).rstrip("0").rstrip("."))
        gs[order[info.codepoint]].draw(TransformPen(pen, (s, 0, 0, -s, x0 + (x + pos.x_offset) * s, baseline - pos.y_offset * s)))
        d.append(pen.getCommands()); x += pos.x_advance + tracking * upm
    return " ".join(c for c in d if c), x * s


def parts(cfg):
    return [(m.group(2) or m.group(3), bool(m.group(2))) for m in re.finditer(r"(<b>(.*?)</b>)|([^<]+)", cfg["brandHtml"])]


def lockup(cfg, t, dark, tld=True, claim=None):
    """Bildzeichen links, Schriftzug rechts. dark = für dunklen Untergrund."""
    ink = "#FFFFFF" if dark else t["ink"]; muted = t["sign-muted"] if dark else t["muted"]
    accent = t["brand-ab-dark"] if dark else t["brand-ab"]
    acc = t.get("mark", t["signal"])
    if dark and cfg.get("logoDarkFree"):   # auf dunklem Grund steht das Zeichen frei, ohne Kachel
        x0, y0, x1, y1 = marks.EXTENT[cfg["mark"]]; s = 176 / (y1 - y0)
        body = '<g transform="translate(%.2f %.2f) scale(%.4f)">%s</g>' % (-x0 * s, 100 - (y0 + y1) / 2 * s, s, marks.glyph(cfg["mark"], "#FFFFFF", acc))
        x = (x1 - x0) * s + 38
    else:
        body = '<g>%s</g>' % marks.tile(cfg["mark"], t["sign-hi"], t["sign-lo"], acc)
        x = 244
    size, base = (136, 118) if claim else (168, 152)
    tx = x
    for txt, hot in parts(cfg):
        d, w = outline(txt, "ssc", 800, size, x, base); body += '<path d="%s" fill="%s"/>' % (d, accent if hot else ink); x += w
    if tld:
        d, w = outline(cfg["tld"], "ssc", 700, size, x, base); body += '<path d="%s" fill="%s"/>' % (d, muted); x += w
    if claim:
        d, w = outline(claim, "ss", 600, 45, tx + 2, 178, 0.012); body += '<path d="%s" fill="%s"/>' % (d, muted); x = max(x, tx + 2 + w)
    return marks.svg(round(x + 6), 200, body)


OG = '''<!DOCTYPE html><html><head><meta charset="utf-8"><style>
@font-face{font-family:"SSC";src:url("file://%(root)s/assets/fonts/ssc-latin.woff2") format("woff2");font-weight:600 900}
@font-face{font-family:"SS";src:url("file://%(root)s/assets/fonts/ss-latin.woff2") format("woff2");font-weight:400 700}
*{box-sizing:border-box}body{margin:0;width:1200px;height:630px;background:linear-gradient(150deg,%(hi)s 0%%,%(sign)s 46%%,%(lo)s 100%%);color:#fff;position:relative;overflow:hidden;font-family:SS}
.key{position:absolute;inset:18px;border:5px solid rgba(255,255,255,.93);border-radius:34px}
.in{position:absolute;inset:0;padding:68px 84px}
.logo{display:flex;align-items:center;gap:20px;height:84px}
.plate{width:84px;height:84px;border-radius:22px;background:#fff;display:grid;place-items:center;flex:none}
.plate svg{width:74px;height:74px}
.name{font:800 62px/1 SSC;letter-spacing:.2px}.name b{font-weight:inherit;color:%(signal)s}.name i{font-style:normal;font-weight:700;color:%(muted)s}
h1{font:800 114px/.95 SSC;margin:58px 0 26px;letter-spacing:-.6px}
p{font:400 40px/1.25 SS;color:%(muted)s;margin:0;max-width:720px}
.g{position:absolute;right:%(gr)spx;bottom:%(gb)spx;width:%(gw)spx;height:%(gw)spx}
</style></head><body><div class="key"></div>
<svg class="g" viewBox="0 0 200 200">%(glyph)s</svg>
<div class="in"><div class="logo"><span class="plate"><svg viewBox="0 0 200 200">%(plate)s</svg></span><span class="name">%(name)s</span></div>
<h1>Falsch getankt?<br>Motor aus lassen.</h1><p>Wir pumpen den Tank direkt vor Ort ab. Rund um die Uhr.</p></div></body></html>'''


SHEET = '''<!DOCTYPE html><html lang="de"><head><meta charset="utf-8"><style>
@font-face{font-family:"SSC";src:url("file://%(root)s/assets/fonts/ssc-latin.woff2") format("woff2");font-weight:600 900}
@font-face{font-family:"SS";src:url("file://%(root)s/assets/fonts/ss-latin.woff2") format("woff2");font-weight:400 700}
*{box-sizing:border-box}body{margin:0;width:1600px;background:%(paper)s;color:%(ink)s;font:400 22px/1.45 SS;padding:56px 64px 52px}
h1{font:800 58px/1 SSC;margin:0 0 12px}.sub{font-size:24px;color:%(muted)s;margin:0 0 38px;max-width:1180px}
h2{font:700 19px/1.2 SS;color:%(muted)s;margin:34px 0 12px}
.top{display:grid;grid-template-columns:320px 1fr;gap:28px 48px;align-items:start}
.mark{width:320px;height:320px;display:block}
.col{display:grid;gap:16px}
.panel{border-radius:22px;padding:30px 38px;display:flex;align-items:center;min-height:150px}
.light{background:#fff;box-shadow:inset 0 0 0 1.5px %(line)s}.dark{background:linear-gradient(150deg,%(hi)s,%(lo)s)}
.panel img{height:88px;display:block;max-width:100%%}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.row{display:flex;align-items:flex-end;gap:26px;flex-wrap:wrap}
.cell{display:grid;gap:9px;justify-items:start;font:600 16px/1.2 SS;color:%(muted)s}
.cell svg{display:block}
.box{background:#fff;border-radius:22px;padding:26px 30px;box-shadow:inset 0 0 0 1.5px %(line)s}
.grid3{display:grid;grid-template-columns:1.25fr 1fr;gap:16px}
.mono{display:flex;gap:16px}.mono div{flex:1;border-radius:18px;display:grid;place-items:center;height:150px}
.mono svg{width:112px;height:112px}
.hdr{display:flex;align-items:center;gap:11px;height:70px;padding:0 22px;border-radius:16px;background:%(paper)s;box-shadow:inset 0 0 0 1.5px %(line)s}
.hdr svg{width:42px;height:42px;flex:none}.hdr span{font:800 31px/1 SSC;letter-spacing:.2px;white-space:nowrap}.hdr b{font-weight:inherit;color:%(ab)s}.hdr i{font-style:normal;font-weight:700;color:%(muted)s}
</style></head><body>
<h1>%(title)s</h1>
<p class="sub">%(note)s</p>
<div class="top"><div><svg class="mark" viewBox="0 0 200 200">%(tile)s</svg></div>
<div class="col"><div class="panel light"><img src="file://%(hell)s" alt=""></div><div class="panel dark"><img src="file://%(dunkel)s" alt=""></div>%(extra)s</div></div>
<div class="grid3"><div><h2>Funktioniert auch ganz klein: App-Symbol, Lesezeichen, Browser-Tab</h2><div class="box"><div class="row">%(sizes)s</div></div></div>
<div><h2>Einfarbig, zum Beispiel für Stempel oder Folie</h2><div class="mono"><div style="background:#fff;box-shadow:inset 0 0 0 1.5px %(line)s">%(black)s</div><div style="background:#16191C">%(white)s</div></div></div></div>
<h2>So steht es oben auf der Website</h2><div class="row"><div class="hdr"><svg viewBox="0 0 200 200">%(tile2)s</svg><span>%(name)s</span></div></div>
<h2>Auf der Website folgt das Zeichen dem gewählten Farbthema</h2><div class="box"><div class="row">%(themes)s</div></div>
</body></html>'''


async def overview(b, cfg, t, out):
    """Übersicht als Bild: Zeichen, Schriftzüge, kleine Größen, einfarbig, Farbthemen."""
    name = cfg["brand"]; mark = cfg["mark"]; acc = t.get("mark", t["signal"])
    def tile(gid, th=t, **k):
        return marks.tile(mark, th["sign-hi"], th["sign-lo"], th.get("mark", th["signal"]), gid=gid, **k)
    sizes = "".join('<div class="cell"><svg width="%d" height="%d" viewBox="0 0 200 200">%s</svg>%d px</div>' % (px, px, tile("s%d" % px), px) for px in (128, 96, 64, 48, 32, 24, 16))
    themes = "".join('<div class="cell"><svg width="104" height="104" viewBox="0 0 200 200">%s</svg>%s</div>' % (tile("th" + k, th), htmlmod.escape(th["name"])) for k, th in THEMES.items())
    extra = ""
    if cfg.get("claim") or not cfg.get("logoTld", True):
        cells = []
        if cfg.get("claim"): cells.append('<div class="panel light"><img style="height:76px" src="file://%s" alt=""></div>' % (out / ("logo-%s-claim-hell.svg" % name)))
        if not cfg.get("logoTld", True): cells.append('<div class="panel light"><img style="height:70px" src="file://%s" alt=""></div>' % (out / ("logo-%s-de-hell.svg" % name)))
        extra = '<div class="two">%s</div>' % "".join(cells)
    page = SHEET % dict(root=ROOT, paper=t["paper"], ink=t["ink"], muted=t["muted"], line=t["line-strong"], hi=t["sign-hi"], lo=t["sign-lo"], ab=t["brand-ab"],
                        title="Logo %s" % cfg.get("display", name), note=htmlmod.escape(cfg.get("markNote", marks.NAMES[mark] + ".")),
                        tile=tile("big"), tile2=tile("hd"), hell=out / ("logo-%s-hell.svg" % name), dunkel=out / ("logo-%s-dunkel.svg" % name), extra=extra,
                        sizes=sizes, themes=themes, name=cfg["brandHtml"] + "<i>%s</i>" % cfg["tld"],
                        black='<svg viewBox="0 0 200 200">%s</svg>' % marks.glyph(mark, "#111111", "#111111"), white='<svg viewBox="0 0 200 200">%s</svg>' % marks.glyph(mark, "#FFFFFF", "#FFFFFF"))
    f = TMP / ("sheet-%s.html" % name); f.write_text(page, encoding="utf-8")
    pg = await b.new_page(viewport={"width": 1600, "height": 900}); await pg.goto("file://%s" % f); await pg.wait_for_timeout(450)
    await pg.screenshot(path=str(out / ("logo-%s-uebersicht.png" % name)), full_page=True); await pg.close()


async def shot(b, html_or_path, out, w, h, transparent=False):
    pg = await b.new_page(viewport={"width": w, "height": h})
    if isinstance(html_or_path, pathlib.Path):
        await pg.goto("file://%s" % html_or_path); await pg.wait_for_timeout(350)
    else:
        await pg.set_content(html_or_path)
    await pg.screenshot(path=str(out), omit_background=transparent); await pg.close()


def shrink(path, colors=256):
    """PNG auf eine Farbpalette bringen. Die Verläufe haben weniger als 256 Stufen, das Bild bleibt deshalb sauber."""
    from PIL import Image
    im = Image.open(path).convert("RGB").quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(path, optimize=True)


async def svg_png(b, svg_text, out, w, h=None, transparent=True):
    vw, vh = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg_text).groups()); h = h or round(w * vh / vw)
    page = '<html><body style="margin:0;background:transparent">%s</body></html>' % svg_text.replace('<svg ', '<svg style="display:block;width:%dpx;height:%dpx" ' % (w, h), 1)
    await shot(b, page, out, w, h, transparent)


async def site(b, cfg):
    name = cfg["brand"]; mark = cfg["mark"]
    # 1) App-Symbole und Teilen-Bild für jedes Farbthema
    for key, t in THEMES.items():
        d = ROOT / "assets/brand" / name / key; d.mkdir(parents=True, exist_ok=True)
        acc = t.get("mark", t["signal"])
        full = marks.svg(200, 200, marks.tile(mark, t["sign-hi"], t["sign-lo"], acc, rx=0, scale=.9))
        mask = marks.svg(200, 200, marks.tile(mark, t["sign-hi"], t["sign-lo"], acc, rx=0, scale=.7))
        for svg_text, fn, px in ((full, "icon-180.png", 180), (mask, "icon-192.png", 192), (mask, "icon-512.png", 512)):
            await svg_png(b, svg_text, d / fn, px, px, False); shrink(d / fn)
        tab = marks.svg(200, 200, marks.tile(mark, t["sign-hi"], t["sign-lo"], acc))     # Symbol im Browser-Tab: Kachel mit runden Ecken
        (d / "icon.svg").write_text(tab, encoding="utf-8")
        await svg_png(b, tab, d / "icon-96.png", 96, 96, True)
        brand_html = cfg["brandHtml"] + "<i>%s</i>" % cfg["tld"]
        big = dict(gr=38, gb=30, gw=330) if mark == "zapf" else dict(gr=52, gb=44, gw=360)
        og = TMP / ("og-%s-%s.html" % (name, key))
        og.write_text(OG % dict(root=ROOT, hi=t["sign-hi"], sign=t["sign"], lo=t["sign-lo"], signal=t["signal"], muted=t["sign-muted"],
                                glyph=marks.glyph(mark, "#fff", acc), plate=marks.glyph(mark, t["sign"], t["sign"] if mark == "puls" else acc),
                                name=brand_html, **big), encoding="utf-8")
        await shot(b, og, d / "og.png", 1200, 630); shrink(d / "og.png")
    # 2) Logo-Dateien im Farbthema der Website
    t = THEMES[cfg.get("logoTheme", "petrol")]; acc = t.get("mark", t["signal"])
    out = ROOT / "logo" / name; out.mkdir(parents=True, exist_ok=True)
    files = {}
    with_tld = cfg.get("logoTld", True)
    files["logo-%s-hell" % name] = lockup(cfg, t, False, with_tld)
    files["logo-%s-dunkel" % name] = lockup(cfg, t, True, with_tld)
    if not with_tld:
        files["logo-%s-de-hell" % name] = lockup(cfg, t, False, True)
        files["logo-%s-de-dunkel" % name] = lockup(cfg, t, True, True)
    if cfg.get("claim"):
        files["logo-%s-claim-hell" % name] = lockup(cfg, t, False, False, cfg["claim"])
        files["logo-%s-claim-dunkel" % name] = lockup(cfg, t, True, False, cfg["claim"])
    files["zeichen-%s" % name] = marks.svg(200, 200, marks.tile(mark, t["sign-hi"], t["sign-lo"], acc))
    files["zeichen-%s-frei" % name] = marks.svg(200, 200, marks.glyph(mark, t["sign"], acc))
    files["zeichen-%s-schwarz" % name] = marks.svg(200, 200, marks.glyph(mark, "#111111", "#111111"))
    files["zeichen-%s-weiss" % name] = marks.svg(200, 200, marks.glyph(mark, "#FFFFFF", "#FFFFFF"))
    for stem, text in files.items():
        (out / (stem + ".svg")).write_text(text, encoding="utf-8")
        await svg_png(b, text, out / (stem + ".png"), 1024 if stem.startswith("zeichen") else 2400)
    profil = marks.svg(200, 200, marks.tile(mark, t["sign-hi"], t["sign-lo"], acc, rx=0, scale=.78))
    await svg_png(b, profil, out / ("profilbild-%s.png" % name), 1024, 1024, False); shrink(out / ("profilbild-%s.png" % name))
    await overview(b, cfg, t, out)
    print("ok", name, "| Zeichen:", mark, "| Logo-Thema:", cfg.get("logoTheme", "petrol"), "|", len(files) * 2 + 1, "Logo-Dateien,", len(THEMES), "Themen")


async def main(paths):
    base = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    cfgs = []
    for p in paths:
        c = dict(base, **json.loads(pathlib.Path(p).read_text(encoding="utf-8"))); c.setdefault("mark", "zapf"); cfgs.append(c)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--allow-file-access-from-files"])
        for cfg in cfgs:
            await site(b, cfg)
        await b.close()


if __name__ == "__main__":
    args = sys.argv[1:] or sorted(str(p) for p in (ROOT / "sites").glob("*.json"))
    asyncio.run(main(args))
