"""Erzeugt je Farbthema Tab-Symbol (SVG) und App-Symbole (PNG) aus den Logo-Vorlagen."""
import asyncio, json, pathlib
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
themes = json.loads((ROOT / "src/themes.json").read_text(encoding="utf-8"))
full = (ROOT / "logo/out/icon-vollflaeche.svg").read_text(encoding="utf-8")
mask = (ROOT / "logo/out/icon-maskable.svg").read_text(encoding="utf-8")
out = ROOT / "assets/icons"
def paint(svg, t):
    return svg.replace("#11636F", t["sign-hi"]).replace("#06323B", t["sign-lo"]).replace("#FF8A1F", t.get("mark", t["signal"]))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for key, t in themes.items():
            fav = paint(full, t)
            (out / ("%s.svg" % key)).write_text(fav, encoding="utf-8")
            for svg, size in ((fav, 180), (paint(mask, t), 192), (paint(mask, t), 512)):
                pg = await b.new_page(viewport={"width": size, "height": size})
                await pg.set_content('<html><body style="margin:0">%s</body></html>' % svg.replace("<svg ", '<svg style="display:block;width:%dpx;height:%dpx" ' % (size, size), 1))
                await pg.screenshot(path=str(out / ("%s-%d.png" % (key, size)))); await pg.close()
            print("ok", key)
        await b.close()
asyncio.run(main())
