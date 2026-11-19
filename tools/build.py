#!/usr/bin/env python3
"""Baut die Website aus src/.
   build.py preview [site.json]     -> dist/ (Vorschau mit Testschnittstelle, noindex)
   build.py site <site.json> <out>  -> fertige Website für eine Domain
   Logo, App-Symbole und Teilen-Bild kommen aus assets/brand/ (erzeugt von tools/brand.py), die Karte aus src/map.svg (tools/karte.py)."""
import json, re, sys, html as htmlmod, urllib.parse, pathlib, shutil, hashlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import marks

ROOT = pathlib.Path(__file__).resolve().parent.parent
DARK = ("--brand-ab:#FF8A1F;--paper:#051A1E;--surface:#0A2A31;--tint:#0F363E;--ink:#EAF3F1;--muted:#9FB9BC;--line:#1A424A;--line-strong:#356B75;"
        "--sign:#0C4C57;--sign-hi:#136876;--sign-lo:#083A43;--board:#0A323A;--foot-a:#062A31;--foot-b:#041D22;--link:#7AD3DF;"
        "--danger:#FF9B8C;--danger-bg:#3B1713;--ok:#7BDCA8;--ok-bg:#0E3525;"
        "--shadow:0 18px 50px rgba(0,0,0,.55);--shadow-card:0 1px 2px rgba(0,0,0,.35),0 16px 36px -22px rgba(0,0,0,.8);"
        "--shadow-sign:0 2px 4px rgba(0,0,0,.3),0 30px 60px -30px rgba(0,0,0,.85);color-scheme:dark")
def strip(s):
    return re.sub(r"\s+", " ", htmlmod.unescape(re.sub(r"<[^>]+>", "", s))).strip()

ALWAYS = ("sign", "sign-hi", "sign-lo", "sign-muted", "board", "foot-a", "foot-b", "signal", "signal-hi", "signal-lo", "signal-press", "on-signal")
LIGHT = ("brand-ab", "link", "tint", "paper", "line", "line-strong", "muted", "ink")

def theme_css(themes):
    """Farbthemen: <html data-theme="..."> wählt eines. Petrol ist der Grundzustand in :root.
       Die Auswahl ist bewusst stärker als die Regel für den Dunkelmodus, damit Schild, Logo und Anruf-Knöpfe auch dort dem Thema folgen."""
    out = []
    for key, t in themes.items():
        if key == "petrol":
            continue
        sel = 'html:root[data-theme="%s"]' % key
        out.append(sel + "{" + "".join("--%s:%s;" % (v, t[v]) for v in ALWAYS) + ("--mark:%s;" % t["mark"] if "mark" in t else "") + "}")
        out.append("@media (prefers-color-scheme:light){" + sel + "{" + "".join("--%s:%s;" % (v, t[v]) for v in LIGHT) + "}}")
        out.append("@media (prefers-color-scheme:dark){" + sel + "{--brand-ab:%s;--link:%s}}" % (t["brand-ab-dark"], t["signal-hi"]))
    # Dunkelmodus der Themen: fast schwarze Flächen mit einem Hauch der Themenfarbe (Petrol behält seine eigenen Werte)
    out.append('@supports (color:color-mix(in srgb,red,blue)){@media (prefers-color-scheme:dark){html:root[data-theme]:not([data-theme="petrol"]){'
               "--paper:color-mix(in srgb,var(--foot-b) 38%,#0A0C0E);--surface:color-mix(in srgb,var(--foot-a) 34%,#14171A);"
               "--tint:color-mix(in srgb,var(--foot-a) 40%,#1D2125);--line:color-mix(in srgb,var(--foot-a) 40%,#2A2F34);"
               "--line-strong:color-mix(in srgb,var(--sign-hi) 40%,#59616A);--muted:color-mix(in srgb,var(--sign-muted) 60%,#8E979F);--ink:#EDF1F4}}}")
    return "\n".join(out)

LANG_ORDER = re.findall(r"'([a-z]{2})'", re.search(r"var LANGS = \[([^\]]+)\]", (ROOT / "src/app.js").read_text(encoding="utf-8")).group(1))

def mix(a, b, wa):
    """wie CSS color-mix(in srgb, a wa, b)"""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join("%02X" % round(x * wa + y * (1 - wa)) for x, y in zip(ca, cb))

def build(cfg, mode, out):
    page = (ROOT / "src/index.html").read_text(encoding="utf-8")
    css = (ROOT / "src/style.css").read_text(encoding="utf-8").replace("/*DARK*/", DARK)
    themes = json.loads((ROOT / "src/themes.json").read_text(encoding="utf-8"))
    css += "\n" + theme_css(themes)
    for k, t in themes.items():  # Leistenfarbe im Dunkelmodus, fest ins HTML, damit sie auch ohne JavaScript stimmt
        t["paper-dark"] = "#051A1E" if k == "petrol" else mix(t["foot-b"], "#0A0C0E", .38)
    if cfg.get("brandVw"):
        css = css.replace("  --brand-ab:#E36C00;", "  --brand-ab:#E36C00;\n  --brand-vw:%s;" % cfg["brandVw"], 1)
    strings = (ROOT / "src/strings.js").read_text(encoding="utf-8")
    geo = (ROOT / "src/geo.js").read_text(encoding="utf-8")
    app = (ROOT / "src/app.js").read_text(encoding="utf-8")
    packs = {f.stem: f.read_text(encoding="utf-8") for f in sorted((ROOT / "src/lang").glob("*.js"))}
    stamp = lambda t: hashlib.sha1((t + cfg["domain"] + cfg.get("alias", "") + mode).encode("utf-8")).hexdigest()[:8]
    jscfg = {"regions": cfg["regions"], "soon": cfg.get("soon", {}), "price": cfg["price"], "waText": cfg["waText"],
             "packs": {k: stamp(t) for k, t in packs.items()}, "langPages": mode == "site"}
    app = app.replace("/*CFG*/", json.dumps(jscfg, ensure_ascii=False))
    if mode == "site":
        app = re.sub(r"\n\s*window\.__tank = .*?;\n", "\n", app)
    theme = cfg.get("theme", "petrol")
    tfile = out / "theme.txt"
    if tfile.exists():
        theme = tfile.read_text(encoding="utf-8").strip() or theme  # im Admin-Bereich gewählt, bleibt beim Neubau erhalten
    if theme not in themes:
        theme = "petrol"
    th = themes[theme]
    mark = cfg.get("mark", "zapf")
    page = page.replace("/*CSS*/", css).replace("/*JS*/", strings + "\n" + geo + "\n" + app)
    page = page.replace("{{MARK_GLYPH}}", marks.glyph_css(mark)).replace("{{MAP_SVG}}", (ROOT / "src/map.svg").read_text(encoding="utf-8").strip())
    url = "https://" + cfg["domain"] + "/"
    canon = cfg.get("canonical", url)
    display = cfg.get("display", cfg["brand"] + cfg["tld"])
    rep = {
        "TITLE": cfg["title"] if mode == "site" else cfg["brand"] + cfg["tld"] + " Vorschau",
        "ROBOTS": "index, follow" if mode == "site" else "noindex, nofollow",
        "CANONICAL": '<link rel="canonical" href="%s">' % canon if mode == "site" else "",
        "OGURL": '<meta property="og:url" content="%s">' % url if mode == "site" else "",
        "OGIMAGE": ('<meta property="og:image" content="%sbrand/%s/og.png">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n<meta property="og:image:type" content="image/png">\n<meta property="og:image:alt" content="%s: Falsch getankt? Motor aus lassen.">\n<meta name="twitter:card" content="summary_large_image">' % (url, theme, htmlmod.escape(display))) if mode == "site" else "",
        "THEME": theme,
        "BRAND": cfg["brand"], "TLD": cfg["tld"], "BRAND_HTML": cfg["brandHtml"], "DISPLAY": display,
        "ALIAS": cfg.get("alias", ""),
        "TC_LIGHT": th["paper"],
        "TC_DARK": th["paper-dark"],
        "C_SIGN": th["sign"], "C_SIGN_HI": th["sign-hi"], "C_SIGN_LO": th["sign-lo"], "C_SIGN_MUTED": th["sign-muted"],
        "C_SIGNAL": th["signal"], "C_ON_SIGNAL": th["on-signal"],
        "MARK_PLATE": marks.glyph(mark, th["sign"], th["sign"] if mark == "puls" else th.get("mark", th["signal"])),
        "REVIEWS_TOTAL": str(sum(cfg.get("reviewCounts", {}).values())),
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
        "@context": "https://schema.org", "@type": "AutomotiveBusiness",
        "name": display, "description": "Mobiler Abpumpservice bei Falschbetankung: Benzin im Diesel, Diesel im Benziner, AdBlue.",
        "url": canon, "telephone": cfg["regions"]["west"]["tel"], "priceRange": "ab %s €" % cfg["price"]["car"],
        "logo": url + "brand/%s/icon-512.png" % theme, "image": url + "brand/%s/og.png" % theme,
        "address": {"@type": "PostalAddress", "streetAddress": cfg["street"], "postalCode": cfg["city"].split(" ")[0],
                    "addressLocality": cfg["city"].split(" ", 1)[1], "addressCountry": "DE"},
        "areaServed": ["Nordrhein-Westfalen", "Hessen", "Rheinland-Pfalz", "Bayern", "Frankfurt am Main", "Rhein-Main-Gebiet"],
        "sameAs": [v for v in cfg.get("reviews", {}).values()],
        "knowsAbout": ["Falschbetankung", "Benzin im Diesel", "Diesel im Benziner", "AdBlue im Dieseltank", "Kraftstoff abpumpen"],
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
    (out / "fonts").mkdir(exist_ok=True)
    for f in (ROOT / "assets/fonts").iterdir():
        shutil.copy2(f, out / "fonts" / f.name)
    brand_dir = ROOT / "assets/brand" / cfg["brand"]
    if not brand_dir.exists():      # Vorschau ohne eigene Website: Material der ersten Website
        brand_dir = sorted(p for p in (ROOT / "assets/brand").iterdir() if p.is_dir())[0]
    # App-Symbole, Teilen-Bild und Manifest für jedes Farbthema: Der Admin-Bereich stellt beim Themenwechsel nur die Verweise um.
    for old_path in ("icons", "site.webmanifest"):
        target = out / old_path
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
    for key, t in themes.items():
        d = out / "brand" / key; d.mkdir(parents=True, exist_ok=True)
        for f in (brand_dir / key).iterdir():
            shutil.copy2(f, d / f.name)
        # favicon.ico (16, 32, 48 px) für Programme, die nur /favicon.ico abfragen (Mail, Lesezeichen, ältere Browser)
        from PIL import Image
        Image.open(brand_dir / key / "icon-512.png").convert("RGBA").save(d / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
        manifest = {"name": display + " – Soforthilfe bei Falschbetankung", "short_name": cfg.get("short", display)[:12], "lang": "de",
                    "start_url": "../../", "scope": "../../", "display": "standalone", "background_color": t["paper"], "theme_color": t["sign"],
                    "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
                              {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]}
        (d / "site.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copy2(brand_dir / theme / "og.png", out / "og.png")   # alte Adresse des Teilen-Bilds bleibt erreichbar
    shutil.copy2(out / "brand" / theme / "favicon.ico", out / "favicon.ico")  # der Admin-Bereich kopiert beide beim Themenwechsel mit
    # Erklärvideo: nur für Websites mit "video": true in sites/*.json; Dateien aus assets/video/<name>/
    vid_dir = ROOT / "assets/video" / cfg["brand"]
    if cfg.get("video") and vid_dir.is_dir():
        (out / "video").mkdir(exist_ok=True)
        for f in vid_dir.iterdir():
            shutil.copy2(f, out / "video" / f.name)
        page = page.replace("  <!--VIDEO-->\n", "").replace("  <!--/VIDEO-->\n", "")
    else:
        page = re.sub(r"  <!--VIDEO-->.*?<!--/VIDEO-->\n\n?", "", page, flags=re.S)
    (out / "index.html").write_text(page, encoding="utf-8")
    # Admin-Bereich: Farbthema wählen (nicht für Suchmaschinen)
    adm = (ROOT / "src/admin.html").read_text(encoding="utf-8")
    repos = cfg.get("adminRepos", [])
    own = "trawigo67-web/" + cfg["domain"].replace(".", "-")
    adm = (adm.replace("{{THEMES_JSON}}", json.dumps(themes, ensure_ascii=False))
              .replace("{{REPOS_JSON}}", json.dumps(repos)).replace("{{OWN_REPO}}", json.dumps(own if own in repos else (repos[0] if repos else own)))
              .replace("{{DISPLAY}}", htmlmod.escape(display)).replace("{{THEME}}", theme))
    (out / "admin").mkdir(exist_ok=True)
    (out / "admin" / "index.html").write_text(adm, encoding="utf-8")
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
    # Sprachseiten (/en/, /tr/ …): fertig übersetzt, damit Google jede Sprache findet (nur auf der veröffentlichten Website)
    if mode == "site":
        import langpages
        canon_b = canon if canon.endswith("/") else canon + "/"
        base_src = i18n
        for k, v in rep.items():
            base_src = base_src.replace("{{%s}}" % k, v)
        pack_out = [(out / "lang" / (c + ".js")).read_text(encoding="utf-8") for c in packs]
        I = langpages.load_i18n(base_src, pack_out)
        langs = ["de"] + [l for l in LANG_ORDER if l != "de" and l in I]
        urls = langpages.lang_urls(canon_b, langs)
        alt = langpages.hreflang_tags(urls) if canon_b == url else ""
        names = langpages.lang_names(page)
        root_page = langpages.footer_links(page)
        if alt:
            root_page = re.sub(r'(<link rel="canonical" href="[^"]*">)', lambda m: m.group(1) + "\n" + alt, root_page, count=1)
        (out / "index.html").write_text(root_page, encoding="utf-8")
        for l in langs[1:]:
            lp = langpages.make(root_page, l, I[l], names, urls, urls[l], l == "ar")
            left = [k for k in re.findall(r'data-i18n="([^"]+)"', page) if k not in I[l]]
            if left:
                sys.exit("Sprachseite %s: fehlende Übersetzungen %s" % (l, sorted(set(left))[:8]))
            (out / l).mkdir(exist_ok=True)
            (out / l / "index.html").write_text(lp, encoding="utf-8")
        lang_list = langs[1:]
    else:
        lang_list = []
    # Unterseiten (Ratgeber, Kosten, Einsatzgebiete): eigene Adressen mit Inhalt, der ohne JavaScript lesbar ist
    import pages as pagesmod
    base_css = (css.split("/* Karte:")[0]).replace('url("fonts/', 'url("/fonts/') + "\n" + theme_css(themes)
    plist = pagesmod.pages(cfg)
    canon_base = canon if canon.endswith("/") else canon + "/"
    for p in plist:
        d = out / p["slug"]; d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(pagesmod.render(cfg, p, base_css, theme, url, canon_base, display, cfg["brandHtml"], plist, tc=(th["paper"], th["paper-dark"])), encoding="utf-8")
    if mode == "site":
        urls = [url] + [url + l + "/" for l in lang_list] + [url + p["slug"] + "/" for p in plist]
        if canon_base == url:
            (out / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n'
                % "".join("  <url><loc>%s</loc></url>\n" % u for u in urls), encoding="utf-8")
        else:  # Zweitadresse: verweist per Canonical auf die Hauptadresse, deshalb nur die Startseite
            (out / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>%s</loc></url>\n</urlset>\n' % url, encoding="utf-8")
    if mode == "site":
        (out / "CNAME").write_text(cfg["domain"] + "\n", encoding="utf-8")
        (out / ".nojekyll").write_text("", encoding="utf-8")
        (out / "theme.txt").write_text(theme + "\n", encoding="utf-8")
        (out / "robots.txt").write_text("User-agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: %ssitemap.xml\n" % url, encoding="utf-8")
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
        if len(sys.argv) > 2:
            base.update(json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8")))
        build(base, "preview", ROOT / "dist")
