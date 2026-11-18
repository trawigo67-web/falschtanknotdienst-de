#!/usr/bin/env python3
"""Erzeugt src/geo.js: vereinfachte Grenzen der 16 Bundesländer für die Standort-Weiche.
   Quelle: Natural Earth 1:10m Admin-1 (gemeinfrei), Auszug in assets/geo/de-states-ne10m.geojson.
   Gemeinsame Grenzen werden für beide Nachbarn identisch vereinfacht, damit keine Lücken entstehen.
   Aufruf: python3 -I tools/geo.py"""
import json, math, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/geo/de-states-ne10m.geojson"
OUT = ROOT / "src/geo.js"
SERVICE = {"BY", "NW", "HE", "RP"}
TOL_FINE, TOL_COARSE = 0.45, 1.6          # Kilometer
KX, KY = 71.5, 111.2                       # km je Grad (Länge bei ~50° N, Breite)
PREC = 1000                                # 0,001° ≈ 70–110 m

def km(p):
    return (p[0] * KX, p[1] * KY)

def dp(pts, tol):
    """Douglas-Peucker, Endpunkte bleiben erhalten."""
    if len(pts) < 3:
        return list(pts)
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = km(pts[a]); bx, by = km(pts[b])
        dx, dy = bx - ax, by - ay
        L = dx * dx + dy * dy
        best, bi = -1.0, -1
        for i in range(a + 1, b):
            px, py = km(pts[i])
            if L == 0:
                d = math.hypot(px - ax, py - ay)
            else:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
                d = math.hypot(px - (ax + t * dx), py - (ay + t * dy))
            if d > best:
                best, bi = d, i
        if best > tol:
            keep[bi] = True
            stack.append((a, bi)); stack.append((bi, b))
    return [p for p, k in zip(pts, keep) if k]

def load_states():
    """Liest die Länder ein: Kürzel -> Liste von Ringen (Punkte als (Länge, Breite))."""
    data = json.loads(SRC.read_text(encoding="utf-8"))
    states = {}
    for f in data["features"]:
        code = f["properties"]["code"].split("-")[1]
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        rings = []
        for poly in polys:
            for r in poly:
                pts = [(round(x, 6), round(y, 6)) for x, y in r]
                if pts[0] == pts[-1]:
                    pts = pts[:-1]
                rings.append(pts)
        states[code] = rings
    return states


def simplify_states(states, tol_for):
    """Vereinfacht alle Ringe. tol_for(Menge der Länder an einem Bogen) -> Toleranz in Kilometern."""
    # Welche Länder teilen sich einen Punkt?
    owners = {}
    for code, rings in states.items():
        for r in rings:
            for p in r:
                owners.setdefault(p, set()).add(code)
    sig = {p: frozenset(s) for p, s in owners.items()}

    def simplify_arc(arc, closed):
        s = sig[arc[1]] if len(arc) > 2 else sig[arc[0]]
        tol = tol_for(s)
        if closed:
            # geschlossener Ring ohne Knoten: kanonischer Start und Richtung
            i = min(range(len(arc)), key=lambda k: arc[k])
            ring = arc[i:] + arc[:i]
            if ring[1] > ring[-1]:
                ring = [ring[0]] + ring[:0:-1]
            j = max(range(1, len(ring)), key=lambda k: (ring[k][0] - ring[0][0]) ** 2 + (ring[k][1] - ring[0][1]) ** 2)
            a = dp(ring[: j + 1], tol); b = dp(ring[j:] + [ring[0]], tol)
            return a[:-1] + b[:-1]
        rev = arc[0] > arc[-1]
        seq = arc[::-1] if rev else arc
        res = dp(seq, tol)
        return res[::-1] if rev else res

    out = {}
    for code, rings in states.items():
        new_rings = []
        for r in rings:
            n = len(r)
            # Knoten: Punkt, dessen Besitzermenge sich von der des Vorgängers oder Nachfolgers unterscheidet
            nodes = [i for i in range(n) if sig[r[i]] != sig[r[i - 1]] or sig[r[i]] != sig[r[(i + 1) % n]]]
            # nur echte Knoten: Punkte, an denen mehr Länder zusammenkommen als auf den Bögen davor/danach
            nodes = [i for i in nodes if len(sig[r[i]]) > min(len(sig[r[i - 1]]), len(sig[r[(i + 1) % n]])) or sig[r[i - 1]] != sig[r[(i + 1) % n]]]
            if not nodes:
                simp = simplify_arc(r, True)
            else:
                simp = []
                for k, a in enumerate(nodes):
                    b = nodes[(k + 1) % len(nodes)]
                    arc = r[a: b + 1] if b > a else r[a:] + r[: b + 1]
                    if len(nodes) == 1:
                        arc = r[a:] + r[:a] + [r[a]]
                    s = simplify_arc(arc, False)
                    simp.extend(s[:-1])
            if len(simp) >= 3:
                new_rings.append(simp)
        out[code] = new_rings
    return out


def main():
    states = load_states()
    out = simplify_states(states, lambda s: TOL_FINE if (s & SERVICE) else TOL_COARSE)

    def enc_num(v):
        v = ~(v << 1) if v < 0 else (v << 1)
        s = ""
        while v >= 0x20:
            s += chr((0x20 | (v & 0x1F)) + 63); v >>= 5
        return s + chr(v + 63)

    def enc_ring(r):
        s, px, py = "", 0, 0
        for x, y in r:
            ix, iy = round(x * PREC), round(y * PREC)
            s += enc_num(ix - px) + enc_num(iy - py); px, py = ix, iy
        return s

    order = ["BE", "HB", "HH", "SL", "BY", "HE", "NW", "RP", "BW", "NI", "TH", "SN", "ST", "BB", "MV", "SH"]
    js = {c: [enc_ring(r) for r in out[c]] for c in order}
    npts = {c: sum(len(r) for r in out[c]) for c in order}
    body = json.dumps(js, ensure_ascii=True, separators=(",", ":"))
    OUT.write_text("/* Erzeugt von tools/geo.py aus Natural Earth 1:10m (gemeinfrei). Nicht von Hand ändern. */\nvar GEO_STATES = %s;\n" % body, encoding="utf-8")
    raw = sum(sum(len(r) for r in states[c]) for c in order)
    print("Punkte roh:", raw, "| vereinfacht:", sum(npts.values()), "|", {c: npts[c] for c in ("BY", "HE", "NW", "RP")}, "| geo.js:", OUT.stat().st_size, "Bytes")
    (ROOT / "assets/geo/de-states-simplified.json").write_text(json.dumps({c: out[c] for c in order}), encoding="utf-8")

if __name__ == "__main__":
    main()
