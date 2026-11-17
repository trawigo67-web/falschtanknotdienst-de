import sys, asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for w in [320, 344, 360, 375, 390, 412, 430, 540, 768, 1024, 1280, 1536]:
            for lang in ["de", "en", "tr"]:
                ctx = await b.new_context(viewport={"width": w, "height": 800}, is_mobile=w < 700, has_touch=w < 700)
                pg = await ctx.new_page(); await pg.goto("http://localhost:8765/index.html"); await pg.wait_for_timeout(250)
                if lang != "de": await pg.evaluate("window.__tank.setLang('%s')" % lang); await pg.wait_for_timeout(120)
                r = await pg.evaluate("""() => { const vw = document.documentElement.clientWidth; const bad = [];
                  for (const p of document.querySelectorAll('.case-panel')) p.hidden = false;
                  document.querySelectorAll('main *, header *, footer *').forEach(e => { const r = e.getBoundingClientRect(); if (r.width && (r.right > vw + 0.5 || r.left < -0.5)) bad.push(e.tagName + '.' + String(e.className.baseVal ?? e.className).slice(0, 30) + ' ' + Math.round(r.left) + '-' + Math.round(r.right)); });
                  return { vw, sw: document.documentElement.scrollWidth, bad: bad.slice(0, 6), h: document.documentElement.scrollHeight } }""")
                flag = "OK " if (r["sw"] <= r["vw"] and not r["bad"]) else "!! "
                print(flag, w, lang, r)
                await ctx.close()
        await b.close()
asyncio.run(main())
