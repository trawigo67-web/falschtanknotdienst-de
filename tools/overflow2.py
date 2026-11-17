import sys, asyncio
from playwright.async_api import async_playwright
SITES = sys.argv[1:]
async def main():
    ok = bad = 0
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for site in SITES:
            for w in [320, 344, 360, 375, 390, 412, 430, 540, 600, 768, 940, 1024, 1080, 1280, 1536]:
                for lang in ["de", "en", "tr"]:
                    ctx = await b.new_context(viewport={"width": w, "height": 800}, is_mobile=w < 700, has_touch=w < 700)
                    pg = await ctx.new_page(); errs = []
                    pg.on("pageerror", lambda e: errs.append(str(e)))
                    await pg.goto("http://localhost:8766/%s/index.html" % site); await pg.wait_for_timeout(200)
                    if lang != "de":
                        await pg.evaluate("document.querySelector('.lang-list button[data-lang=\"%s\"]').click()" % lang); await pg.wait_for_timeout(100)
                    r = await pg.evaluate("""() => { const vw = document.documentElement.clientWidth; const bad = [];
                      for (const p of document.querySelectorAll('.case-panel')) p.hidden = false;
                      document.querySelectorAll('main *, header *, footer *').forEach(e => { if (e.closest('.lang-list')) return; const r = e.getBoundingClientRect(); if (r.width && (r.right > vw + 0.5 || r.left < -0.5)) bad.push(e.tagName + '.' + String(e.className.baseVal ?? e.className).slice(0, 30) + ' ' + Math.round(r.left) + '-' + Math.round(r.right)); });
                      const hr = document.querySelector('.header-row').getBoundingClientRect(); const br = document.querySelector('.brand').getBoundingClientRect(); const lg = document.querySelector('.lang').getBoundingClientRect();
                      return { vw, sw: document.documentElement.scrollWidth, bad: bad.slice(0, 5), gap: Math.round(lg.left - br.right), lang: document.documentElement.lang } }""")
                    good = r["sw"] <= r["vw"] and not r["bad"] and r["gap"] >= 6 and r["lang"] == lang and not errs
                    ok += good; bad += (not good)
                    if not good: print("!!", site, w, lang, r, errs[:2])
                    await ctx.close()
        await b.close()
    print("Breiten-Check:", ok, "ok,", bad, "fehlerhaft")
asyncio.run(main())
