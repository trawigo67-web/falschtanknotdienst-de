#!/usr/bin/env python3
"""Baut die Website aus src/.
   build.py preview                 -> dist/ (Vorschau, noindex)
   build.py site <site.json> <out>  -> fertige Website für eine Domain"""
import json, re, sys, html as htmlmod, urllib.parse, pathlib, shutil, hashlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DARK = ("--brand-ab:#FF8A1F;--paper:#051A1E;--surface:#0A2A31;--tint:#0F363E;--ink:#EAF3F1;--muted:#9FB9BC;--line:#1A424A;--line-strong:#356B75;"
        "--sign:#0C4C57;--sign-hi:#136876;--sign-lo:#083A43;--board:#0A323A;--foot-a:#062A31;--foot-b:#041D22;--link:#7AD3DF;"
        "--danger:#FF9B8C;--danger-bg:#3B1713;--ok:#7BDCA8;--ok-bg:#0E3525;"
        "--shadow:0 18px 50px rgba(0,0,0,.55);--shadow-card:0 1px 2px rgba(0,0,0,.35),0 16px 36px -22px rgba(0,0,0,.8);"
        "--shadow-sign:0 2px 4px rgba(0,0,0,.3),0 30px 60px -30px rgba(0,0,0,.85);color-scheme:dark")
FAVICON = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'><rect width='200' height='200' rx='46' fill='#0B4650'/>"
    "<g transform='translate(100 100) scale(.9) translate(-113 -125)'><path d='M139 50A64 64 0 0 1 87.8 166.9' fill='none' stroke='#FF8A1F' stroke-width='17' stroke-linecap='round'/>"
    "<path d='M98.4 144 53.6 155.8 83 191.6z' fill='#FF8A1F'/><g transform='translate(-6 -9) rotate(-24 108 92)' fill='none' stroke='#fff' stroke-linecap='round' stroke-linejoin='round'>"
    "<rect x='82' y='60' width='66' height='36' rx='11' fill='#fff' stroke='none'/><rect x='141' y='65' width='17' height='26' rx='6' fill='#fff' stroke='none'/>"
    "<path d='M84 78H65q-9 0-13 8l-7 13' stroke-width='17'/><path d='M98 96v20a11 11 0 0 0 11 11h18a11 11 0 0 0 11-11V96' stroke-width='10'/></g></g></svg>")

def strip(s):
    return re.sub(r"\s+", " ", htmlmod.unescape(re.sub(r"<[^>]+>", "", s))).strip()

def build(cfg, mode, out):
    page = (ROOT / "src/index.html").read_text(encoding="utf-8")
    css = (ROOT / "src/style.css").read_text(encoding="utf-8").replace("/*DARK*/", DARK)
    if cfg.get("brandVw"):
        css = css.replace("  --brand-ab:#E36C00;", "  --brand-ab:#E36C00;\n  --brand-vw:%s;" % cfg["brandVw"], 1)
    strings = (ROOT / "src/strings.js").read_text(encoding="utf-8")
    geo = (ROOT / "src/geo.js").read_text(encoding="utf-8")
    app = (ROOT / "src/app.js").read_text(encoding="utf-8")
    packs = {f.stem: f.read_text(encoding="utf-8") for f in sorted((ROOT / "src/lang").glob("*.js"))}
    stamp = lambda t: hashlib.sha1((t + cfg["domain"] + cfg.get("alias", "") + mode).encode("utf-8")).hexdigest()[:8]
    jscfg = {"regions": cfg["regions"], "soon": cfg.get("soon", {}), "price": cfg["price"], "waText": cfg["waText"],
             "packs": {k: stamp(t) for k, t in packs.items()}}
    app = app.replace("/*CFG*/", json.dumps(jscfg, ensure_ascii=False))
    if mode == "site":
        app = re.sub(r"\n\s*window\.__tank = .*?;\n", "\n", app)
    page = page.replace("/*CSS*/", css).replace("/*JS*/", strings + "\n" + geo + "\n" + app)

    url = "https://" + cfg["domain"] + "/"
    canon = cfg.get("canonical", url)
    display = cfg.get("display", cfg["brand"] + cfg["tld"])
    rep = {
        "TITLE": cfg["title"] if mode == "site" else cfg["brand"] + cfg["tld"] + " Vorschau",
        "ROBOTS": "index, follow" if mode == "site" else "noindex, nofollow",
        "CANONICAL": '<link rel="canonical" href="%s">' % canon if mode == "site" else "",
        "OGURL": '<meta property="og:url" content="%s">' % url if mode == "site" else "",
        "OGIMAGE": ('<meta property="og:image" content="%sog.png">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n<meta name="twitter:card" content="summary_large_image">' % url) if mode == "site" else "",
        "BRAND": cfg["brand"], "TLD": cfg["tld"], "BRAND_HTML": cfg["brandHtml"], "DISPLAY": display,
        "ALIAS": cfg.get("alias", ""),
        "FAVICON": "data:image/svg+xml," + urllib.parse.quote(FAVICON, safe="/:=' ,()-."),
        "WEST_TEL": cfg["regions"]["west"]["tel"], "WEST_NUM": cfg["regions"]["west"]["num"], "WEST_WA": cfg["regions"]["west"]["wa"],
        "RM_TEL": cfg["regions"]["rm"]["tel"], "RM_NUM": cfg["regions"]["rm"]["num"], "RM_WA": cfg["regions"]["rm"]["wa"],
        "BY_TEL": cfg["regions"]["by"]["tel"], "BY_NUM": cfg["regions"]["by"]["num"], "BY_WA": cfg["regions"]["by"]["wa"],
        "WA_TEXT": urllib.parse.quote(cfg["waText"]),
        "PRICE_CAR": cfg["price"]["car"], "PRICE_CAMPER": cfg["price"]["camper"],
        "REVIEWS_WEST": htmlmod.escape(cfg["reviews"]["west"]), "REVIEWS_BY": htmlmod.escape(cfg["reviews"]["by"]),
        "COMPANY": cfg["company"], "COMPANY_SHORT": cfg["companyShort"], "OWNER": cfg["owner"],
        "STREET": cfg["street"], "CITY": cfg["city"],
        "OFFICE_TEL": cfg["officeTel"], "OFFICE_NUM": cfg["officeNum"], "EMAIL": cfg["email"],
    }
    if not rep["ALIAS"]:  # ohne zweite Adresse entfällt der Hinweis
        page = re.sub(r'<span data-i18n="footer\.alias">.*?</span> ', "", page)
        page = re.sub(r'\n\s*"footer\.alias": "[^"]*",', "", page)
    faq = re.findall(r'<summary><span data-i18n="faq\.q\d+">(.*?)</span>.*?</summary>\s*<p data-i18n="faq\.a\d+">(.*?)</p>', page, re.S)
    ld = [{
        "@context": "https://schema.org", "@type": ["AutomotiveBusiness", "EmergencyService"],
        "name": display, "description": "Mobiler Abpumpservice bei Falschbetankung: Benzin im Diesel, Diesel im Benziner, AdBlue.",
        "url": url, "telephone": cfg["regions"]["west"]["tel"], "priceRange": "ab %s €" % cfg["price"]["car"],
        "address": {"@type": "PostalAddress", "streetAddress": cfg["street"], "postalCode": cfg["city"].split(" ")[0],
                    "addressLocality": cfg["city"].split(" ", 1)[1], "addressCountry": "DE"},
        "areaServed": ["Nordrhein-Westfalen", "Hessen", "Rheinland-Pfalz", "Bayern"],
        "openingHoursSpecification": {"@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "00:00", "closes": "23:59"},
        "contactPoint": [
            {"@type": "ContactPoint", "telephone": cfg["regions"]["west"]["tel"], "contactType": "emergency", "areaServed": ["DE-NW", "DE-HE", "DE-RP"], "availableLanguage": ["de", "en", "tr"]},
            {"@type": "ContactPoint", "telephone": cfg["regions"]["rm"]["tel"], "contactType": "emergency", "areaServed": ["DE-HE", "DE-RP"], "availableLanguage": ["de", "en", "tr"]},
            {"@type": "ContactPoint", "telephone": cfg["regions"]["by"]["tel"], "contactType": "emergency", "areaServed": "DE-BY", "availableLanguage": ["de", "en", "tr"]},
        ],
    }, {"@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in faq]}]
    rep["JSONLD"] = '<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    for k, v in rep.items():
        page = page.replace("{{%s}}" % k, v)
    left = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", page)))
    if left:
        sys.exit("Unersetzte Platzhalter: %s" % left)
    keys = set(re.findall(r'data-i18n(?:-aria|-ph)?="([^"]+)"', page))
    i18n = strings.split("var CHAT")[0]
    have = {}
    for lang in ("de", "en", "tr"):
        block = re.search(r"\n  %s: \{(.*?)\n  \}" % lang, i18n, re.S).group(1)
        have[lang] = set(re.findall(r'^\s*"([^"]+)":', block, re.M))
    for lang in ("en", "tr"):
        miss = sorted(keys - have[lang])
        if miss:
            sys.exit("Fehlende Übersetzung (%s): %s" % (lang, miss))
        only = sorted((have["de"] - have[lang]) | ({k for k in have[lang] if k.startswith(("loc.", "st."))} - have["de"] - keys))
        if only:
            sys.exit("Schlüssel nur in einer Sprache (%s): %s" % (lang, only))
    chat = "var CHAT" + strings.split("var CHAT")[1]
    ck = {}
    for lang in ("de", "en", "tr"):
        block = re.search(r"\n  %s: \{(.*?)\n  \}" % lang, chat, re.S).group(1)
        ck[lang] = set(re.findall(r'^\s*"([^"]+)":', block, re.M))
    for lang in ("en", "tr"):
        d = sorted(ck["de"] ^ ck[lang])
        if d:
            sys.exit("Chat-Schlüssel weichen ab (%s): %s" % (lang, d))

    out.mkdir(parents=True, exist_ok=True)
    for sub in ("fonts", "icons"):
        (out / sub).mkdir(exist_ok=True)
        for f in (ROOT / "assets" / sub).iterdir():
            shutil.copy2(f, out / sub / f.name)
    manifest = {"name": display + " – Soforthilfe bei Falschbetankung", "short_name": cfg.get("short", display)[:12], "lang": "de",
                "start_url": "./", "display": "standalone", "background_color": "#EEF3F2", "theme_color": "#0B4650",
                "icons": [{"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
                          {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]}
    (out / "site.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "index.html").write_text(page, encoding="utf-8")
    # Sprachpakete, die erst bei Bedarf geladen werden
    (out / "lang").mkdir(exist_ok=True)
    for code, text in packs.items():
        for k, val in rep.items():
            text = text.replace("{{%s}}" % k, val)
        if not rep["ALIAS"]:
            text = re.sub(r'\n\s*"footer\.alias": "[^"]*",', "", text)
        rest = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", text)))
        if rest:
            sys.exit("Unersetzte Platzhalter im Sprachpaket %s: %s" % (code, rest))
        (out / "lang" / (code + ".js")).write_text(text, encoding="utf-8")
    if mode == "site":
        (out / "CNAME").write_text(cfg["domain"] + "\n", encoding="utf-8")
        (out / ".nojekyll").write_text("", encoding="utf-8")
        (out / "robots.txt").write_text("User-agent: *\nAllow: /\n\nSitemap: %ssitemap.xml\n" % url, encoding="utf-8")
        (out / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>%s</loc></url>\n</urlset>\n' % url, encoding="utf-8")
        nf = (ROOT / "src/404.html").read_text(encoding="utf-8")
        for k, v in rep.items():
            nf = nf.replace("{{%s}}" % k, v)
        (out / "404.html").write_text(nf, encoding="utf-8")
        (out / "README.md").write_text("# %s\n\nWebsite %s (Abpumpservice bei Falschbetankung, IG-Trade24 Germany).\nStatische Seite, veröffentlicht über GitHub Pages. Die Dateien in diesem Zweig sind das fertige Ergebnis. Quelltexte und Build-Skripte liegen im Zweig `quelle` des Repositorys falschtanknotdienst-de.\n" % (cfg["domain"], cfg["domain"]), encoding="utf-8")
    print("ok", mode, out, "%d KB" % (len(page.encode("utf-8")) // 1024), "| FAQ:", len(faq), "| i18n-Keys:", len(keys))

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    base = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    if mode == "site":
        base.update(json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8")))
        build(base, "site", pathlib.Path(sys.argv[3]))
    else:
        build(base, "preview", ROOT / "dist")
