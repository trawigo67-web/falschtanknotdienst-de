import sys, asyncio
from playwright.async_api import async_playwright
JOBS = [  # (svg, out, w, h, transparent)
 ("logo/out/zeichen.svg", "logo/png/zeichen-1024.png", 1024, 1024, True),
 ("logo/out/profilbild.svg", "logo/png/profilbild-1024.png", 1024, 1024, False),
 ("logo/out/logo-hell.svg", "logo/png/logo-hell-2400.png", 2400, None, True),
 ("logo/out/logo-dunkel.svg", "logo/png/logo-dunkel-2400.png", 2400, None, True),
 ("logo/out/icon-vollflaeche.svg", "dist/icons/icon-180.png", 180, 180, False),
 ("logo/out/icon-maskable.svg", "dist/icons/icon-512.png", 512, 512, False),
 ("logo/out/icon-maskable.svg", "dist/icons/icon-192.png", 192, 192, False),
]
async def main():
    import re, pathlib
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--allow-file-access-from-files"])
        for svg, out, w, h, tr in JOBS:
            src = pathlib.Path(svg).read_text(encoding="utf-8"); vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', src); vw, vh = float(vb.group(1)), float(vb.group(2))
            hh = h or round(w * vh / vw)
            pg = await b.new_page(viewport={"width": w, "height": hh})
            await pg.set_content('<html><body style="margin:0;background:transparent">%s</body></html>' % src.replace('<svg ', '<svg style="display:block;width:%dpx;height:%dpx" ' % (w, hh), 1))
            await pg.screenshot(path=out, omit_background=tr); await pg.close(); print("png", out, w, hh)
        pg = await b.new_page(viewport={"width": 1600, "height": 1040}, device_scale_factor=1)
        await pg.goto("file:///home/claude/site/logo/sheet.html"); await pg.wait_for_timeout(500)
        await pg.screenshot(path="logo/png/logo-uebersicht.png"); print("sheet ok")
        await b.close()
asyncio.run(main())
