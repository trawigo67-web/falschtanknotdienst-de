#!/usr/bin/env python3
"""Bildzeichen „Tropfen mit Puls“ (Tankdoktor) als ein einziger Pfad.
   Der Tropfen steht für den Kraftstoff, die Pulslinie für den Doktor. Die Linie ist aus dem Tropfen ausgeschnitten,
   damit das Zeichen auf jedem Untergrund und in jeder Farbe funktioniert (Kachel, Papier, Folie fürs Fahrzeug).
   Aufruf: python3 tools/zeichen.py  -> gibt den Pfad aus (steht als Konstante in tools/marks.py)."""
import math
from pathops import Path, PathOp, LineCap, LineJoin, ArcSize, Direction, op

CX, CY, R, H, TIP = 100.0, 120.0, 52.0, 96.0, 6.0   # Kreis unten, Spitze oben, Rundung der Spitze
BASE, WIDTH = CY + 3.0, 12.0                         # Grundlinie und Stärke der Pulslinie
PULSE = [(-1.2, 0), (-.46, 0), (-.22, -.66), (.08, .58), (.30, -.24), (.44, 0), (1.2, 0)]  # in Einheiten von R

def drop():
    phi = math.asin(R / H); px, py = R * math.cos(phi), -R * math.sin(phi)
    d = TIP / math.sin(phi); my = CY - H + d; ax, ay = TIP * math.cos(phi), -TIP * math.sin(phi)
    p = Path()
    p.moveTo(CX + ax, my + ay); p.lineTo(CX + px, CY + py)
    p.arcTo(R, R, 0, ArcSize.LARGE, Direction.CW, CX - px, CY + py)
    p.lineTo(CX - ax, my + ay)
    p.arcTo(TIP, TIP, 0, ArcSize.SMALL, Direction.CW, CX + ax, my + ay)
    p.close()
    p.convertConicsToQuads()
    return p

def pulse():
    p = Path()
    for i, (x, y) in enumerate(PULSE):
        (p.moveTo if i == 0 else p.lineTo)(CX + x * R, BASE + y * R)
    p.stroke(WIDTH, LineCap.BUTT_CAP, LineJoin.ROUND_JOIN, 4)
    p.convertConicsToQuads()
    return p

def fmt(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")

def svg_path(path):
    path.convertConicsToQuads()
    out = []
    for verb, pts in path.segments:
        if verb == "moveTo": out.append("M%s %s" % (fmt(pts[0][0]), fmt(pts[0][1])))
        elif verb == "lineTo": out.append("L%s %s" % (fmt(pts[0][0]), fmt(pts[0][1])))
        elif verb == "qCurveTo":
            # fontTools-Schreibweise: mehrere Stützpunkte mit gedachten Zwischenpunkten
            for i in range(len(pts) - 1):
                c = pts[i]; e = pts[i + 1] if i == len(pts) - 2 else ((pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2)
                out.append("Q%s %s %s %s" % (fmt(c[0]), fmt(c[1]), fmt(e[0]), fmt(e[1])))
        elif verb == "curveTo": out.append("C" + " ".join("%s %s" % (fmt(x), fmt(y)) for x, y in pts))
        elif verb == "closePath": out.append("Z")
    return "".join(out)

if __name__ == "__main__":
    mark = op(drop(), pulse(), PathOp.DIFFERENCE)
    d = svg_path(mark)
    print(d)
    print("# Länge:", len(d), "Zeichen; Fläche:", round(abs(mark.area)), "; Grenzen:", [round(v, 1) for v in mark.bounds])
