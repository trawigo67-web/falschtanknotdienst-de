#!/usr/bin/env python3
"""Erzeugt src/map.svg: kleine Deutschlandkarte mit den drei Einsatzgebieten für den Abschnitt „Hier sind wir im Einsatz“.
   Quelle wie bei der Standort-Weiche: Natural Earth 1:10m (gemeinfrei). Die Zonen folgen config.json (soon: Mittelpunkt und Radius).
   Die Farben kommen aus dem Farbthema der Seite (CSS-Klassen m-o, m-w, m-b, m-z in style.css).
   Aufruf: python3 -I tools/karte.py"""
import json, math, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from geo import load_states, simplify_states, KX, KY

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "src/map.svg"
TOL = 3.2                       # Kilometer: grob genug für eine kleine Karte
MIN_AREA = 130.0                # km²: kleinere Inseln entfallen
LON0, LAT1, W = 5.72, 55.12, 300.0
SPAN_KM = (15.12 - LON0) * KX   # Breite der Karte in Kilometern
K = W / SPAN_KM                 # Einheiten je Kilometer
H = round((LAT1 - 47.22) * KY * K)
WEST, BY = ("NW", "HE", "RP"), ("BY",)
CITIES = [("Köln", 50.938, 6.960, "r"), ("Dortmund", 51.514, 7.465, "r"), ("Nürnberg", 49.452, 11.077, "r"), ("München", 48.137, 11.575, "r")]


def xy(lon, lat):
    return ((lon - LON0) * KX * K, (LAT1 - lat) * KY * K)


def area_km2(r):
    s = 0.0
    for i in range(len(r)):
        x1, y1 = r[i][0] * KX, r[i][1] * KY; x2, y2 = r[(i + 1) % len(r)][0] * KX, r[(i + 1) % len(r)][1] * KY
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def path(rings):
    """Kompakter Pfad mit relativen ganzzahligen Schritten (Raster 0,5 Einheiten ≈ 1,1 km)."""
    out = []
    for r in rings:
        pts = []
        for lon, lat in r:
            x, y = xy(lon, lat); p = (round(x * 2), round(y * 2))
            if not pts or p != pts[-1]:
                pts.append(p)
        if len(pts) > 1 and pts[0] == pts[-1]:
            pts.pop()
        if len(pts) < 3:
            continue
        nums = []; px, py = pts[0]
        for x, y in pts[1:]:
            nums += [x - px, y - py]; px, py = x, y
        d = "M%s %s" % (fmt(pts[0][0]), fmt(pts[0][1])); seg = "l" + fmt(nums[0]) + "".join(sep(v) for v in nums[1:])
        out.append(d + seg + "z")
    return "".join(out)


def fmt(v):
    """halbe Einheiten als Zahl: 7 -> 3.5"""
    s = "%g" % (v / 2)
    return s.replace("0.", ".") if s.startswith(("0.", "-0.")) else s


def sep(v):
    s = fmt(v)
    return s if s.startswith("-") else " " + s


def main():
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    simp = simplify_states(load_states(), lambda s: TOL)
    rings = {c: [r for r in rs if area_km2(r) >= MIN_AREA] for c, rs in simp.items()}
    others = [c for c in rings if c not in WEST + BY]
    zones = []
    for z in cfg.get("soon", {}).values():
        x, y = xy(z["center"][1], z["center"][0]); zones.append((x, y, z["radiusKm"] * K))
    fx, fy = xy(8.682, 50.111)
    body = ['<g class="m-o"><path d="%s"/></g>' % path([r for c in others for r in rings[c]])]
    body.append('<g class="m-w">%s</g>' % "".join('<path d="%s"/>' % path(rings[c]) for c in WEST))
    body.append('<g class="m-zr">%s</g>' % "".join('<circle cx="%.1f" cy="%.1f" r="%.1f"/>' % (x, y, r + 1.6) for x, y, r in zones))
    body.append('<g class="m-z">%s</g>' % "".join('<circle cx="%.1f" cy="%.1f" r="%.1f"/>' % z for z in zones))
    body.append('<g class="m-b"><path d="%s"/></g>' % path(rings["BY"]))
    dots, labels = [], ['<text class="m-tz" x="%.1f" y="%.1f" text-anchor="middle">Frankfurt</text>' % (fx, fy + 3.6)]
    for name, lat, lon, side in CITIES:
        x, y = xy(lon, lat)
        dots.append('<circle cx="%.1f" cy="%.1f" r="2.7"/>' % (x, y))
        labels.append('<text x="%.1f" y="%.1f">%s</text>' % (x + 6, y + 3.7, name))
    body.append('<g class="m-c">%s</g><g class="m-t">%s</g>' % ("".join(dots), "".join(labels)))
    svg = '<svg class="map-svg" viewBox="0 0 %d %d" aria-hidden="true" focusable="false">%s</svg>\n' % (W, H, "".join(body))
    OUT.write_text(svg, encoding="utf-8")
    n = {c: sum(len(r) for r in rs) for c, rs in rings.items()}
    print("Karte:", OUT.stat().st_size, "Bytes | Punkte:", sum(n.values()), "| Einsatzländer:", {c: n[c] for c in WEST + BY}, "| Größe: %d x %d" % (W, H))


if __name__ == "__main__":
    main()
