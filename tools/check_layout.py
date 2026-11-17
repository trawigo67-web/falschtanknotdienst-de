"""Layout-Prüfung: kein seitliches Scrollen, nichts ragt aus Buttons, auch nach der Standortfreigabe.
   python3 tools/check_layout.py falschtanknotdienst.de tankdoktor.de   (Server: out/ auf :8766, dist/ auf :8765)"""
import sys, asyncio
from playwright.async_api import async_playwright
SITES = sys.argv[1:]
WIDTHS = [320, 344, 360, 375, 390, 412, 430, 540, 600, 768, 940, 1024, 1080, 1280, 1536]
FIXES = [("BY", 48.137, 11.575), ("HE+bald", 50.111, 8.682), ("NW", 50.938, 6.960), ("BW", 48.776, 9.183), ("MV", 54.090, 12.140), ("Ausland", 47.377, 8.540)]
JS = """() => { const vw = document.documentElement.clientWidth; const bad = [];
  for (const p of document.querySelectorAll('.case-panel')) p.hidden = false;
  document.querySelectorAll('main *, header *, footer *').forEach(e => { if (e.closest('.lang-list')) return; const r = e.getBoundingClientRect(); if (r.width && (r.right > vw + 0.5 || r.left < -0.5)) bad.push(e.tagName + '.' + String(e.className.baseVal ?? e.className).slice(0, 30) + ' ' + Math.round(r.left) + '-' + Math.round(r.right)); });
  document.querySelectorAll('.btn-call, .loc-btn, .btn, .case-tab, .sheet-row, .soon-tag, .callpanel-soon').forEach(b => { const br = b.getBoundingClientRect(); if (!br.width) return;
    b.querySelectorAll('*').forEach(c => { const r = c.getBoundingClientRect(); if (r.width && (r.right > br.right + 0.5 || r.left < br.left - 0.5 || r.bottom > br.bottom + 0.5 || r.top < br.top - 0.5)) bad.push('ragt heraus: ' + String(b.className).slice(0, 24) + ' > ' + String(c.className.baseVal ?? c.className).slice(0, 20)); }); });
  const hr = document.querySelector('.header-row').getBoundingClientRect(); const br = document.querySelector('.brand').getBoundingClientRect(); const lg = document.querySelector('.lang').getBoundingClientRect();
  const small = [...document.querySelectorAll('main a, main button, .stickybar a, .stickybar button, header button, header a')].filter(e => { const r = e.getBoundingClientRect(); return r.width && r.height && (r.height < 43.5) && !e.closest('.legal') && !e.classList.contains('textlink') && !e.closest('p') ; }).map(e => String(e.className).slice(0, 24) + ' ' + Math.round(e.getBoundingClientRect().height));
  return { vw, sw: document.documentElement.scrollWidth, bad: bad.slice(0, 6), small: small.slice(0, 4), gap: Math.round(document.documentElement.dir === 'rtl' ? br.left - lg.right : lg.left - br.right), lang: document.documentElement.lang,
    visibleCalls: [...document.querySelectorAll('#callpanel .btn-call')].filter(a => !a.classList.contains('is-other')).length } }"""
async def main():
    ok = bad = 0
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        async def run(url, w, lang, fix=None, label=""):
            nonlocal ok, bad
            ctx = await b.new_context(viewport={"width": w, "height": 800}, is_mobile=w < 700, has_touch=w < 700, locale="de-DE")
            pg = await ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.goto(url); await pg.wait_for_timeout(180)
            if lang != "de":
                await pg.evaluate("document.querySelector('.lang-list button[data-lang=\"%s\"]').click()" % lang)
                await pg.wait_for_function("document.documentElement.lang === '%s'" % lang, timeout=6000); await pg.wait_for_timeout(120)
            if fix:
                await pg.evaluate("([a,b]) => window.__tank.setFix(a,b)", [fix[1], fix[2]]); await pg.wait_for_timeout(80)
            r = await pg.evaluate(JS)
            good = r["sw"] <= r["vw"] and not r["bad"] and not r["small"] and r["gap"] >= 6 and r["lang"] == lang and not errs
            if fix and fix[0] in ("BY", "HE+bald", "NW"): good = good and r["visibleCalls"] == 1
            if fix and fix[0] in ("BW", "MV", "Ausland"): good = good and r["visibleCalls"] == 2
            ok += good; bad += (not good)
            if not good: print("!!", label, w, lang, r, errs[:2])
            await ctx.close()
        LANGS = ["de", "en", "tr", "ar", "ru", "uk", "pl", "ro"]
        for i, site in enumerate(SITES):
            for w in (WIDTHS if i == 0 else [320, 360, 390, 768, 1280]):
                for lang in LANGS:
                    await run("http://localhost:8766/%s/index.html" % site, w, lang, None, site)
        for w in [320, 360, 390, 768, 1280]:
            for lang in LANGS:
                for fx in (FIXES if lang in ("de", "ar", "ru") else [FIXES[0], FIXES[1], FIXES[4]]):
                    await run("http://localhost:8765/", w, lang, fx, "Standort " + fx[0])
        await b.close()
    print("Layout-Prüfung:", ok, "ok,", bad, "fehlerhaft")
    sys.exit(1 if bad else 0)
asyncio.run(main())
