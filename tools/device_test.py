"""Gerätetest mit Android- und iPhone-Profilen (Chrome-Engine, Geräteprofile von Playwright).
   Prüft Darstellung, Anruf-Links, Standort-Weiche (simulierte Standorte), Gebietsauswahl und Chat.
   python3 tools/device_test.py <site-ordner>   (Server: out/ auf :8766)"""
import asyncio, sys, json, urllib.parse
from playwright.async_api import async_playwright
from PIL import Image
SITE = sys.argv[1] if len(sys.argv) > 1 else "falschtanknotdienst.de"
URL = "http://localhost:8766/%s/index.html" % SITE
DEVICES = [a for a in sys.argv[2:] if a != "-v"] or ["iPhone SE (3rd gen)", "iPhone 13 Mini", "iPhone 15", "iPhone 15 Pro Max", "Galaxy S9+", "Galaxy S24", "Galaxy A55", "Pixel 7"]
MUC = {"latitude": 48.137, "longitude": 11.575}; FFM = {"latitude": 50.111, "longitude": 8.682}; CGN = {"latitude": 50.938, "longitude": 6.960}; STR = {"latitude": 48.776, "longitude": 9.183}
fails = []
VERBOSE = "-v" in sys.argv
def check(dev, name, cond, info=""):
    if VERBOSE: print("   ", "ok " if cond else "!! ", name, flush=True)
    if not cond: fails.append("%s: %s %s" % (dev, name, info))
    return cond

async def hero_state(pg):
    return await pg.evaluate("""() => { const q = s => document.querySelector(s); const vis = [...document.querySelectorAll('#callpanel .btn-call')].filter(a => !a.classList.contains('is-other'));
      const r = e => { const b = e.getBoundingClientRect(); return [Math.round(b.top), Math.round(b.bottom)]; };
      return { loc: document.documentElement.getAttribute('data-loc'), title: q('#callpanel .loc-title').textContent, status: q('#callpanel .loc-status').hidden ? '' : q('#callpanel .loc-status').textContent,
        main: vis.map(a => ({ href: a.getAttribute('href'), where: a.querySelector('.where').textContent, label: a.querySelector('.call-label').textContent, box: r(a) })),
        other: [...document.querySelectorAll('#callpanel .btn-call.is-other')].map(a => a.getAttribute('href')), locBox: r(q('#callpanel .loc-btn')),
        vh: innerHeight, vw: innerWidth, sw: document.documentElement.scrollWidth, wa: q('#callpanel [data-open-sheet=wa]').getAttribute('href') }; }""")

async def run_device(p, b, name, shots):
    d = p.devices[name]
    # 1) ohne Freigabe laden
    ctx = await b.new_context(**d, locale="de-DE")
    pg = await ctx.new_page(); errs = []; pg.set_default_timeout(8000)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" and "ERR_FAILED" not in m.text else None)
    await pg.goto(URL); await pg.wait_for_timeout(500)
    st = await hero_state(pg)
    check(name, "kein seitliches Scrollen", st["sw"] <= st["vw"], st)
    check(name, "Start: drei Nummern", len(st["main"]) == 3 and st["main"][0]["href"] == "tel:+491742432222" and st["main"][1]["href"] == "tel:+491704044555" and st["main"][2]["href"] == "tel:+4915211303570", st["main"])
    check(name, "Start: Beschriftung Jetzt anrufen", all(m["label"] == "Jetzt anrufen" for m in st["main"]))
    check(name, "Standort-Knopf im ersten Bildschirm", st["locBox"][1] <= st["vh"], st["locBox"])
    check(name, "erste Nummer im ersten Bildschirm", st["main"][0]["box"][1] <= st["vh"], (st["main"][0]["box"], st["vh"]))
    fold2 = st["main"][1]["box"][0] < st["vh"]
    await pg.screenshot(path="/tmp/neu/dev-%s.png" % name.replace(" ", "_").replace("(", "").replace(")", "").replace("+", "plus")); shots.append((name, "/tmp/neu/dev-%s.png" % name.replace(" ", "_").replace("(", "").replace(")", "").replace("+", "plus"), fold2))
    # 2) Freigabe verweigert
    await pg.tap("#callpanel [data-locate]"); await pg.wait_for_timeout(700)
    st = await hero_state(pg)
    check(name, "verweigert: Hinweis und alle Nummern", st["loc"] in ("denied", "fail") and st["status"] != "" and len(st["main"]) == 3, st)
    # 3) Freigabe erteilt: München
    await ctx.grant_permissions(["geolocation"]); await ctx.set_geolocation(MUC)
    await pg.tap("#callpanel [data-locate]"); await pg.wait_for_timeout(700)
    st = await hero_state(pg)
    check(name, "München: nur Bayern-Nummer", st["loc"] == "ok" and len(st["main"]) == 1 and st["main"][0]["href"] == "tel:+491704044555" and st["main"][0]["where"] == "Ihr Einsatzteam für Bayern" and st["title"] == "Bayern", st)
    check(name, "München: andere Nummer bleibt erreichbar", st["other"] == ["tel:+491742432222", "tel:+4915211303570"], st["other"])
    check(name, "München: Nummer im ersten Bildschirm", st["main"][0]["box"][1] <= st["vh"], st["main"][0]["box"])
    # WhatsApp enthält Standort-Link und geht an die Bayern-Nummer
    await pg.evaluate("window.addEventListener('click', e => { const a = e.target.closest && e.target.closest('a[href^=\\'https://wa.me\\']'); if (a) { e.preventDefault(); window.__wa = a.href; } })")
    await pg.tap("#callpanel [data-open-sheet=wa]"); await pg.wait_for_timeout(400)
    href = await pg.evaluate("window.__wa || ''")
    check(name, "WhatsApp: Bayern-Nummer mit Standort-Link", "wa.me/491704044555" in href and "maps.google.com" in urllib.parse.unquote(href) and "48.13700,11.57500" in urllib.parse.unquote(href), href)
    await pg.goto(URL); await pg.wait_for_timeout(700)      # Freigabe besteht: automatisch beim Laden
    st = await hero_state(pg)
    check(name, "erneuter Besuch: automatisch Bayern", st["loc"] == "ok" and len(st["main"]) == 1 and st["main"][0]["href"] == "tel:+491704044555", st)
    # 4) Frankfurt: West-Nummer und Rhein-Main-Hinweis
    await ctx.set_geolocation(FFM); await pg.tap("#callpanel [data-locate]"); await pg.wait_for_timeout(700)
    st = await hero_state(pg)
    check(name, "Frankfurt: Rhein-Main-Team", st["title"] == "Hessen" and len(st["main"]) == 1 and st["main"][0]["href"] == "tel:+4915211303570" and "Rhein-Main" in st["main"][0]["where"], st)
    # 5) Stuttgart: anderes Bundesland, beide Nummern
    await ctx.set_geolocation(STR); await pg.tap("#callpanel [data-locate]"); await pg.wait_for_timeout(700)
    st = await hero_state(pg)
    check(name, "Stuttgart: alle Nummern mit Hinweis", st["title"] == "Baden-Württemberg" and len(st["main"]) == 3 and st["status"] != "", st)
    await ctx.close()

    # 6) Gebietsauswahl über die feste Leiste, Standort im Blatt
    ctx = await b.new_context(**d, locale="de-DE"); pg = await ctx.new_page(); pg.set_default_timeout(8000)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    await pg.goto(URL); await pg.wait_for_timeout(400)
    await pg.evaluate("document.querySelector('#preise').scrollIntoView()"); await pg.wait_for_timeout(700)
    bar = await pg.evaluate("(() => { const b = document.querySelector('#stickybar'); const r = b.getBoundingClientRect(); return { on: b.classList.contains('is-on'), bottom: Math.round(r.bottom), vh: innerHeight, callH: Math.round(b.querySelector('.stickybar-call').getBoundingClientRect().height) }; })()")
    check(name, "feste Anruf-Leiste sichtbar", bar["on"] and bar["bottom"] <= bar["vh"] + 1 and bar["callH"] >= 44, bar)
    await pg.tap("#stickybar .stickybar-call"); await pg.wait_for_timeout(400)
    sh = await pg.evaluate("(() => { const s = document.querySelector('#sheet'); const c = s.querySelector('.sheet-card').getBoundingClientRect(); return { open: !s.hidden, rows: [...s.querySelectorAll('.sheet-row')].filter(r => r.offsetParent).map(r => r.getAttribute('href')), top: Math.round(c.top), bottom: Math.round(c.bottom), vh: innerHeight }; })()")
    check(name, "Gebietsauswahl offen mit vier Zeilen", sh["open"] and sh["rows"] == ["tel:+491742432222", "tel:+491704044555", "tel:+4915211303570", "tel:+491742432222"] and sh["top"] >= 0 and sh["bottom"] <= sh["vh"] + 1, sh)
    await ctx.grant_permissions(["geolocation"]); await ctx.set_geolocation(CGN)
    await pg.tap("#sheet [data-locate]"); await pg.wait_for_timeout(700)
    sh = await pg.evaluate("(() => { const s = document.querySelector('#sheet'); return [...s.querySelectorAll('.sheet-row')].filter(r => r.offsetParent).map(r => r.getAttribute('href')); })()")
    check(name, "Standort im Blatt: nur West-Zeile", sh == ["tel:+491742432222"], sh)
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(200)
    # 7) Chat mit Standortfreigabe
    await ctx.set_geolocation(MUC)
    await pg.evaluate("document.querySelector('#stickybar [data-open-chat]').click()"); await pg.wait_for_timeout(1500)
    chat = await pg.evaluate("(() => { const c = document.querySelector('#chat'); const r = c.getBoundingClientRect(); return { open: !c.hidden, top: Math.round(r.top), bottom: Math.round(r.bottom), vh: innerHeight, sw: document.documentElement.scrollWidth, vw: innerWidth }; })()")
    check(name, "Chat füllt den Bildschirm", chat["open"] and chat["top"] == 0 and abs(chat["bottom"] - chat["vh"]) <= 1 and chat["sw"] <= chat["vw"], chat)
    async def chip(text):
        await pg.locator("#chat .chip", has_text=text).first.tap(); await pg.wait_for_timeout(1500)
    await chip("Benzin im Diesel"); await chip("Nein, der Motor ist aus"); await pg.wait_for_timeout(700); await chip("Pkw")
    res = await pg.evaluate("(() => { const c = document.querySelector('#chat .result'); if (!c) return null; return { call: c.querySelector('.btn-call').getAttribute('href'), wa: decodeURIComponent(c.querySelector('.btn-wa').getAttribute('href')), text: c.innerText.slice(0, 400) }; })()")
    # Standort ist durch die Freigabe im Blatt (Köln) schon bekannt: der Chat fragt nicht mehr nach Gebiet und Ort
    check(name, "Chat: Ergebnis ohne Rückfrage nach dem Gebiet", res is not None and res["call"] == "tel:+491742432222" and "maps.google.com/?q=50.938" in res["wa"] and "Nordrhein-Westfalen" in res["wa"], res)
    await ctx.close()

    # 8) Chat ohne vorherige Freigabe: Standort-Knopf im Chat
    ctx = await b.new_context(**d, locale="de-DE", geolocation=MUC); pg = await ctx.new_page(); pg.set_default_timeout(8000)
    await pg.goto(URL); await pg.wait_for_timeout(400)
    await pg.tap("#callpanel [data-open-chat]"); await pg.wait_for_timeout(1500)
    async def chip2(text):
        await pg.locator("#chat .chip", has_text=text).first.tap(); await pg.wait_for_timeout(1500)
    await chip2("Diesel im Benziner"); await chip2("Ja, der Motor lief"); await pg.wait_for_timeout(900); await chip2("Wohnmobil")
    await ctx.grant_permissions(["geolocation"])
    await chip2("Standort freigeben"); await pg.wait_for_timeout(1800)
    res = await pg.evaluate("(() => { const c = document.querySelector('#chat .result'); if (!c) return null; return { call: c.querySelector('.btn-call').getAttribute('href'), wa: decodeURIComponent(c.querySelector('.btn-wa').getAttribute('href')), log: document.querySelector('#chat-log').innerText.slice(-600) }; })()")
    check(name, "Chat: Standort-Knopf führt zur Bayern-Nummer", res is not None and res["call"] == "tel:+491704044555" and "Bundesland: Bayern" in res["wa"] and "maps.google.com/?q=48.137" in res["wa"] and "Wohnmobil" in res["wa"], res)
    hero = await hero_state(pg)
    check(name, "Chat-Standort gilt auch auf der Seite", hero["loc"] == "ok" and len(hero["main"]) == 1 and hero["main"][0]["href"] == "tel:+491704044555", hero)
    await ctx.close()

    # 9) Sprachwahl über die Flagge: Arabisch (rechts nach links) und Ukrainisch
    ctx = await b.new_context(**d, locale="de-DE"); pg = await ctx.new_page(); pg.set_default_timeout(8000)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    await pg.goto(URL); await pg.wait_for_timeout(400)
    for code, h1part, rtl in (("ar", "المحرك", True), ("uk", "двигун", False), ("de", "Motor aus", False)):
        await pg.tap(".lang-current"); await pg.wait_for_timeout(250)
        await pg.tap(".lang-list [data-lang=%s]" % code)
        await pg.wait_for_function("document.documentElement.lang === '%s'" % code, timeout=6000); await pg.wait_for_timeout(300)
        r = await pg.evaluate("""() => ({ dir: document.documentElement.dir, h1: document.querySelector('h1').innerText, flag: document.querySelector('[data-lang-flag]').getAttribute('href'),
          calls: [...document.querySelectorAll('#callpanel .btn-call')].map(a => a.getAttribute('href')), num: document.querySelector('#callpanel .num').textContent,
          numDir: getComputedStyle(document.querySelector('#callpanel .num')).direction, sw: document.documentElement.scrollWidth, vw: innerWidth, open: document.querySelector('.lang').classList.contains('is-open') })""")
        check(name, "Sprache %s" % code, r["dir"] == ("rtl" if rtl else "ltr") and h1part in r["h1"] and r["flag"] == "#f-" + code and r["calls"] == ["tel:+491742432222", "tel:+491704044555", "tel:+4915211303570"] and r["num"] == "0174 243 22 22" and r["numDir"] == "ltr" and r["sw"] <= r["vw"] and not r["open"], r)
    await ctx.close()
    check(name, "keine Skriptfehler", not errs, errs[:3])

async def main():
    shots = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for name in DEVICES:
            try:
                await run_device(p, b, name, shots)
            except Exception as e:
                fails.append("%s: ABBRUCH %s" % (name, str(e)[:500]))
                if not shots or shots[-1][0] != name: shots.append((name, None, False))
            d = p.devices[name]
            print("%-22s %4dx%-4d dpr %.2f  zweite Nummer beim Start %s" % (name, d["viewport"]["width"], d["viewport"]["height"], d["device_scale_factor"], "sichtbar" if shots[-1][2] else "erst nach Scrollen"))
        await b.close()
    ims = [Image.open(s[1]) for s in shots if s[1]]
    h = 520
    ims = [im.resize((round(im.width * h / im.height), h), Image.LANCZOS) for im in ims]
    sheet = Image.new("RGB", (sum(i.width for i in ims) + 12 * (len(ims) - 1), h), (40, 40, 40)); x = 0
    for im in ims:
        sheet.paste(im, (x, 0)); x += im.width + 12
    sheet.save("/tmp/neu/geraete.png")
    print("Prüfpunkte je Gerät: 24 |", "ALLES OK" if not fails else "%d FEHLER" % len(fails))
    for f in fails: print("  -", f[:600])
    sys.exit(1 if fails else 0)
asyncio.run(main())
