import sys, asyncio
from playwright.async_api import async_playwright
async def main(url, out, w, h, full, scale):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox","--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width":w,"height":h}, device_scale_factor=scale)
        await pg.goto(url); await pg.wait_for_timeout(700)
        await pg.screenshot(path=out, full_page=full)
        await b.close()
url,out,w,h = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
full = (sys.argv[5]=="full") if len(sys.argv)>5 else False
scale = float(sys.argv[6]) if len(sys.argv)>6 else 1
asyncio.run(main(url,out,w,h,full,scale))
