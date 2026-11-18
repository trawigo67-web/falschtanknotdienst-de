"""Eigene Adresse je Sprache (/en/, /tr/, /ar/ …), fertig übersetzt im HTML.

Google indexiert Sprachen, die nur per JavaScript auf derselben Adresse umgeschaltet werden, nicht zuverlässig
(Search Central: „Managing multi-regional and multilingual sites“). Deshalb erzeugt der Build aus der deutschen
Startseite je Sprache eine eigene Seite: Texte aus den Sprachpaketen direkt eingesetzt, eigener Titel, eigene
Beschreibung, Canonical auf sich selbst und hreflang-Verweise auf alle Sprachfassungen.
"""
import html.parser
import json
import re
import subprocess

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
OG_LOCALE = {"de": "de_DE", "en": "en_GB", "tr": "tr_TR", "ar": "ar_AR", "ru": "ru_RU", "uk": "uk_UA", "pl": "pl_PL", "ro": "ro_RO",
             "es": "es_ES", "bg": "bg_BG", "fr": "fr_FR", "it": "it_IT", "sq": "sq_AL", "el": "el_GR"}


def load_i18n(i18n_src, pack_texts):
    """Liest I18N aus strings.js und den Sprachpaketen (Node, damit die JS-Objekte exakt so gelesen werden wie im Browser)."""
    js = r"""
const vm = require('vm'); const ctx = {}; vm.createContext(ctx);
const src = JSON.parse(require('fs').readFileSync(0, 'utf8'));
vm.runInContext('var CHAT = {};\n' + src.base + '\n;this.__I = I18N;', ctx);
for (const t of src.packs) vm.runInContext(t, ctx);
process.stdout.write(JSON.stringify(ctx.__I));
"""
    out = subprocess.run(["node", "-e", js], input=json.dumps({"base": i18n_src, "packs": pack_texts}), capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


class _Spans(html.parser.HTMLParser):
    """Findet zu jedem Element mit data-i18n den Bereich seines Inhalts (Anfang nach dem öffnenden, Ende vor dem schließenden Tag)."""

    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.lines = [0]
        for m in re.finditer("\n", text):
            self.lines.append(m.end())
        self.stack, self.spans = [], []

    def off(self):
        ln, col = self.getpos()
        return self.lines[ln - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self.off()
        end = start + len(self.get_starttag_text())
        if tag in VOID:
            return
        key = dict(attrs).get("data-i18n")
        self.stack.append((tag, key, end))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pos = self.off()
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                t, key, inner_start = self.stack[i]
                del self.stack[i:]
                if key:
                    self.spans.append((inner_start, pos, key))
                return


def translate(page, d):
    """Setzt die Übersetzungen in alle data-i18n-Elemente ein (äußerste gewinnt, wie innerHTML im Browser)."""
    p = _Spans(page)
    p.feed(page)
    spans = sorted(p.spans)
    keep, last_end = [], -1
    for s, e, k in spans:
        if s >= last_end:
            keep.append((s, e, k)); last_end = e
    out, pos = [], 0
    for s, e, k in keep:
        out.append(page[pos:s])
        out.append(d[k] if k in d else page[s:e])
        pos = e
    out.append(page[pos:])
    page = "".join(out)

    def attr(name, key_attr):
        def rep(m):
            tag = m.group(0)
            k = re.search(r'%s="([^"]+)"' % key_attr, tag).group(1)
            if k not in d:
                return tag
            v = d[k].replace("&", "&amp;").replace('"', "&quot;")
            if re.search(r'\s%s="' % name, tag):
                return re.sub(r'(\s%s=")[^"]*(")' % name, lambda mm: mm.group(1) + v + mm.group(2), tag, count=1)
            return tag.replace(" %s=" % key_attr, ' %s="%s" %s=' % (name, v, key_attr), 1)
        return rep
    page = re.sub(r'<[a-zA-Z][^>]*\sdata-i18n-aria="[^"]+"[^>]*>', attr("aria-label", "data-i18n-aria"), page)
    page = re.sub(r'<[a-zA-Z][^>]*\sdata-i18n-ph="[^"]+"[^>]*>', attr("placeholder", "data-i18n-ph"), page)
    return page


def lang_urls(canon_base, langs):
    return {l: canon_base if l == "de" else "%s%s/" % (canon_base, l) for l in langs}


def hreflang_tags(urls):
    tags = ['<link rel="alternate" hreflang="%s" href="%s">' % (l, u) for l, u in urls.items()]
    tags.append('<link rel="alternate" hreflang="x-default" href="%s">' % urls["de"])
    return "\n".join(tags)


def footer_links(page, prefix_de="/"):
    """Sprachwahl im Fuß als echte Links, damit Suchmaschinen den Sprachseiten folgen können."""
    def block(m):
        b = m.group(0)
        b = re.sub(r'<button type="button" data-lang="([a-z]{2})"', lambda mm: '<a href="%s" hreflang="%s" data-lang="%s"' % (
            prefix_de if mm.group(1) == "de" else "/%s/" % mm.group(1), mm.group(1), mm.group(1)), b)
        # Links kennzeichnen die aktuelle Sprache mit aria-current, nicht mit aria-pressed (das gehört zu Knöpfen)
        b = re.sub(r'(<a href="[^"]*" hreflang="[a-z]{2}" data-lang="[a-z]{2}" lang="[a-z]{2}") aria-pressed="(true|false)"',
                   lambda mm: mm.group(1) + (' aria-current="page"' if mm.group(2) == "true" else ""), b)
        return b.replace("</button>", "</a>")
    return re.sub(r'<div class="footer-langs".*?</div>', block, page, count=1, flags=re.S)


def absolutize(page):
    """Relative Adressen (brand/…, fonts/…, video/…) auf die Wurzel beziehen, weil die Sprachseite eine Ebene tiefer liegt."""
    page = re.sub(r'(\s(?:href|src|poster)=")(?!/|#|[a-zA-Z][a-zA-Z0-9+.-]*:)([^"]+")', r"\1/\2", page)
    page = re.sub(r'url\("(?!/|data:|https?:)', 'url("/', page)
    return page


def make(page, l, d, names, urls, canon_self, rtl):
    """Sprachfassung l aus der fertigen deutschen Seite."""
    p = translate(page, d)
    p = re.sub(r'<html lang="de"', '<html lang="%s" dir="%s" data-page-lang="%s"' % (l, "rtl" if rtl else "ltr", l), p, count=1)
    if "meta.title" in d:
        p = re.sub(r"<title>.*?</title>", lambda m: "<title>%s</title>" % htmlesc(d["meta.title"]), p, count=1, flags=re.S)
        p = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + htmlesc(d["meta.title"]), p, count=1)
    if "meta.desc" in d:
        p = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + htmlesc(d["meta.desc"]), p, count=1)
        p = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + htmlesc(d["meta.desc"]), p, count=1)
    p = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="%s">' % canon_self, p, count=1)
    p = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + canon_self, p, count=1)
    p = re.sub(r'(<meta property="og:locale" content=")[^"]*', lambda m: m.group(1) + OG_LOCALE.get(l, l), p, count=1)
    # Sprachwahl: aktuelle Sprache anzeigen
    p = re.sub(r'(data-lang="[a-z]{2}"[^>]*aria-pressed=")(true|false)(")', lambda m: m.group(1) + "false" + m.group(3), p)
    p = re.sub(r'(data-lang="%s"[^>]*aria-pressed=")false(")' % l, r"\1true\2", p)
    p = p.replace(' aria-current="page"', '')
    p = re.sub(r'(<a href="[^"]*" hreflang="%s" data-lang="%s" lang="%s")' % (l, l, l), r'\1 aria-current="page"', p, count=1)
    p = re.sub(r'(<use data-lang-flag href="#f-)[a-z]{2}(")', r"\g<1>%s\2" % l, p, count=1)
    p = re.sub(r'(<span class="lang-name" data-lang-current>)[^<]*', lambda m: m.group(1) + names.get(l, l), p, count=1)
    # Hinweis „Impressum nur auf Deutsch“ zeigen
    p = p.replace('<p class="legal-lang" data-i18n="legal.note" hidden>', '<p class="legal-lang" data-i18n="legal.note">')
    # Fragen-Daten (FAQPage) sind deutsch und passen nicht zum übersetzten Text: auf Sprachseiten weglassen
    def ld(m):
        try:
            data = json.loads(m.group(1).replace("<\\/", "</"))
        except ValueError:
            return m.group(0)
        if isinstance(data, list):
            data = [x for x in data if x.get("@type") != "FAQPage"]
        return '<script type="application/ld+json">%s</script>' % json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    p = re.sub(r'<script type="application/ld\+json">(.*?)</script>', ld, p, flags=re.S)
    return absolutize(p)


def htmlesc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def lang_names(page):
    return {m.group(1): m.group(2) for m in re.finditer(r'<button type="button" data-lang="([a-z]{2})"[^>]*>.*?<span class="name">([^<]+)</span>', page)}
