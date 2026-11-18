"""Bildzeichen der Websites, jeweils im Feld 200 x 200.
   zapf = Zapfpistole, deren Schlauch zum Rückpfeil wird (falschtanknotdienst.de)
   puls = Tropfen mit Pulslinie (tankdoktor.de); der Pfad entsteht in tools/zeichen.py"""

PULS = ("M105 31.8L143.7 91.8Q148.8 99.7 150.8 108.9Q151.7 112.9 151.9 117L126.3 117L120.8 107.5Q119.5 105.4 117.2 104.7"
        "Q114.8 104.1 112.6 105.3Q110.4 106.6 109.8 109L104.5 128.9L94.4 87.3Q93.6 84.1 90.6 83Q88.3 82.2 86 83.2"
        "Q83.8 84.3 82.9 86.6L71.9 117L48.1 117Q48.3 112.9 49.2 108.9Q51.2 99.7 56.3 91.8L95 31.8Q95.8 30.5 97.1 29.8"
        "Q98.5 29.1 100 29.1Q101.5 29.1 102.9 29.8Q104.2 30.5 105 31.8Z"
        "M151.2 129Q149.7 137.4 145.7 144.9Q141.2 153.1 134.1 159.3Q127 165.4 118.2 168.7Q109.4 172 100 172"
        "Q90.6 172 81.8 168.7Q73 165.4 65.9 159.3Q58.8 153.1 54.3 144.9Q50.3 137.4 48.8 129L76.1 129Q80.3 129 81.7 125.1"
        "L87.4 109.4L98.3 154.6Q98.9 157 101 158.3Q103.2 159.6 105.6 159Q109 158.2 110 154.7L117.7 126Q119.4 129 122.9 129L151.2 129Z")

ZAPF = ('<g transform="translate(100 100) scale(.9) translate(-113 -125)">'
        '<path d="M139 50A64 64 0 0 1 87.8 166.9" fill="none" stroke="{a}" stroke-width="15" stroke-linecap="round"/>'
        '<path d="M98.4 144 53.6 155.8 83 191.6z" fill="{a}"/>'
        '<g transform="translate(-6 -9) rotate(-24 108 92)" fill="none" stroke="{c}" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="82" y="60" width="66" height="36" rx="11" fill="{c}" stroke="none"/><rect x="141" y="65" width="17" height="26" rx="6" fill="{c}" stroke="none"/>'
        '<rect x="75" y="66" width="13" height="24" rx="4" fill="{c}" stroke="none"/><path d="M84 78H65q-9 0-13 8l-7 13" stroke-width="15.5"/>'
        '<path d="M98 96v20a11 11 0 0 0 11 11h18a11 11 0 0 0 11-11V96" stroke-width="9.5"/></g></g>')

ZAPF_CSS = ('<g transform="translate(100 100) scale(.9) translate(-113 -125)">'
            '<path d="M139 50A64 64 0 0 1 87.800 166.900" fill="none" style="stroke:var(--mark,var(--signal))" stroke-width="15" stroke-linecap="round"/>'
            '<path d="M98.400 144 53.600 155.800 83 191.600z" style="fill:var(--mark,var(--signal))"/>'
            '<g transform="translate(-6 -9) rotate(-24 108 92)" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">'
            '<rect x="82" y="60" width="66" height="36" rx="11" fill="currentColor" stroke="none"/>'
            '<rect x="141" y="65" width="17" height="26" rx="6" fill="currentColor" stroke="none"/>'
            '<rect x="75" y="66" width="13" height="24" rx="4" fill="currentColor" stroke="none"/>'
            '<path d="M84 78H65q-9 0-13 8l-7 13" stroke-width="15.500"/>'
            '<path d="M98 96v20a11 11 0 0 0 11 11h18a11 11 0 0 0 11-11V96" stroke-width="9.500"/></g></g>')

EXTENT = {"zapf": (33.8, 23.2, 160.8, 160.0), "puls": (48.0, 29.0, 152.0, 172.0)}   # sichtbare Fläche im Feld 200 x 200
NAMES = {"zapf": "Zapfpistole, deren Schlauch zum Rückpfeil wird", "puls": "Tropfen mit Pulslinie"}


def glyph(mark, ink, accent):
    """Zeichen mit festen Farben: ink = Hauptfarbe (bei 'zapf' die Pistole), accent = Signalfarbe (bei 'puls' der Tropfen)."""
    if mark == "puls":
        return '<path d="%s" fill="%s"/>' % (PULS, accent)
    return ZAPF.format(c=ink, a=accent)


def glyph_css(mark):
    """Zeichen für die Seite: Farben kommen aus dem Farbthema (CSS-Variablen)."""
    if mark == "puls":
        return '<path d="%s" style="fill:var(--mark-fill,var(--mark,var(--signal)))"/>' % PULS
    return ZAPF_CSS


def tile(mark, hi, lo, accent, rx=46, scale=1.0, ink="#fff", gid="t"):
    """Kachel mit Verlauf und Zeichen (ohne <svg>-Rahmen)."""
    g = glyph(mark, ink, accent)
    if scale != 1.0:
        g = '<g transform="translate(100 100) scale(%s) translate(-100 -100)">%s</g>' % (scale, g)
    return ('<defs><linearGradient id="%s" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient></defs>'
            '<rect width="200" height="200" rx="%d" fill="url(#%s)"/>%s' % (gid, hi, lo, rx, gid, g))


def svg(w, h, body):
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" width="%s" height="%s">%s</svg>\n' % (w, h, w, h, body)

