import sys, asyncio, json
from playwright.async_api import async_playwright
from PIL import Image

async def run(job):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width": job["w"], "height": job["h"]}, device_scale_factor=job.get("dpr", 1),
                                  is_mobile=job.get("mobile", False), has_touch=job.get("mobile", False),
                                  color_scheme=job.get("scheme", "light"), locale=job.get("locale", "de-DE"))
        pg = await ctx.new_page()
        errors = []
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errors.append(str(e)))
        await pg.goto(job["url"]); await pg.wait_for_timeout(600)
        for step in job.get("steps", []):
            if "js" in step: await pg.evaluate(step["js"])
            if "click" in step: await pg.click(step["click"])
            if "type" in step: await pg.fill(step["sel"], step["type"]); await pg.press(step["sel"], "Enter")
            await pg.wait_for_timeout(step.get("wait", 400))
        out = job["out"]
        await pg.screenshot(path=out, full_page=job.get("full", False))
        info = await pg.evaluate("({sw: document.documentElement.scrollWidth, iw: innerWidth, h: document.documentElement.scrollHeight})")
        await b.close()
        if job.get("cols"):
            im = Image.open(out); W, H = im.size; seg = job.get("seg", 1700 * job.get("dpr", 1)); n = -(-H // seg); gap = 14
            sheets = []
            for s in range(0, n, job["cols"]):
                k = min(job["cols"], n - s)
                sheet = Image.new("RGB", (k * W + (k - 1) * gap, min(seg, H)), (40, 40, 40))
                for i in range(k):
                    part = im.crop((0, (s + i) * seg, W, min(H, (s + i + 1) * seg)))
                    sheet.paste(part, (i * (W + gap), 0))
                name = out.replace(".png", "-%d.png" % (s // job["cols"] + 1)); sheet.save(name); sheets.append(name)
            print("sheets", sheets)
        print(json.dumps({"out": out, "info": info, "errors": errors[:8]}))

asyncio.run(run(json.loads(sys.argv[1])))
