"""Prüft die Standort-Weiche im echten Browser-Code (Vorschau-Build auf :8765)."""
import asyncio, json, sys
from playwright.async_api import async_playwright
CASES = [
 ("München", 48.137, 11.575, "BY"), ("Nürnberg", 49.452, 11.077, "BY"), ("Würzburg", 49.791, 9.953, "BY"), ("Aschaffenburg", 49.974, 9.150, "BY"),
 ("Alzenau", 50.088, 9.066, "BY"), ("Neu-Ulm", 48.393, 10.012, "BY"), ("Lindau", 47.546, 9.684, "BY"), ("Hof", 50.313, 11.913, "BY"), ("Passau", 48.567, 13.432, "BY"),
 ("Coburg", 50.259, 10.964, "BY"), ("Augsburg", 48.371, 10.898, "BY"), ("Regensburg", 49.013, 12.102, "BY"), ("Garmisch", 47.492, 11.096, "BY"), ("Berchtesgaden", 47.630, 13.001, "BY"),
 ("Hanau", 50.134, 8.917, "HE"), ("Frankfurt", 50.111, 8.682, "HE"), ("Darmstadt", 49.873, 8.651, "HE"), ("Wiesbaden", 50.083, 8.240, "HE"), ("Kassel", 51.313, 9.479, "HE"),
 ("Fulda", 50.555, 9.680, "HE"), ("Limburg", 50.384, 8.061, "HE"), ("Gießen", 50.584, 8.678, "HE"), ("Offenbach", 50.096, 8.776, "HE"), ("Lampertheim", 49.596, 8.468, "HE"),
 ("Seligenstadt", 50.044, 8.975, "HE"), ("Flughafen Frankfurt", 50.038, 8.562, "HE"), ("Marburg", 50.802, 8.767, "HE"),
 ("Mainz", 49.993, 8.247, "RP"), ("Koblenz", 50.357, 7.589, "RP"), ("Trier", 49.750, 6.637, "RP"), ("Ludwigshafen", 49.477, 8.445, "RP"), ("Worms", 49.632, 8.359, "RP"),
 ("Kaiserslautern", 49.440, 7.749, "RP"), ("Bad Kreuznach", 49.845, 7.867, "RP"),
 ("Köln", 50.938, 6.960, "NW"), ("Düsseldorf", 51.227, 6.773, "NW"), ("Dortmund", 51.514, 7.465, "NW"), ("Bielefeld", 52.030, 8.532, "NW"), ("Aachen", 50.776, 6.084, "NW"),
 ("Siegen", 50.874, 8.024, "NW"), ("Münster", 51.962, 7.626, "NW"), ("Haan", 51.193, 7.012, "NW"), ("Paderborn", 51.719, 8.757, "NW"), ("Bonn", 50.735, 7.100, "NW"),
 ("Stuttgart", 48.776, 9.183, "BW"), ("Ulm", 48.401, 9.988, "BW"), ("Mannheim", 49.488, 8.467, "BW"), ("Heidelberg", 49.399, 8.672, "BW"), ("Freiburg", 47.999, 7.842, "BW"),
 ("Berlin", 52.520, 13.405, "BE"), ("Potsdam", 52.396, 13.058, "BB"), ("Hamburg", 53.551, 9.994, "HH"), ("Bremen", 53.079, 8.802, "HB"), ("Bremerhaven", 53.540, 8.586, "HB"),
 ("Hannover", 52.376, 9.739, "NI"), ("Osnabrück", 52.280, 8.047, "NI"), ("Göttingen", 51.541, 9.916, "NI"), ("Saarbrücken", 49.240, 6.997, "SL"),
 ("Erfurt", 50.985, 11.030, "TH"), ("Sonneberg", 50.358, 11.174, "TH"), ("Dresden", 51.050, 13.738, "SN"), ("Leipzig", 51.340, 12.375, "SN"),
 ("Magdeburg", 52.131, 11.640, "ST"), ("Schwerin", 53.635, 11.401, "MV"), ("Kiel", 54.323, 10.123, "SH"), ("Sylt", 54.908, 8.318, "SH"), ("Rügen", 54.420, 13.430, "MV"),
 ("Zürich", 47.377, 8.540, None), ("Amsterdam", 52.370, 4.895, None), ("Prag", 50.075, 14.438, None), ("Wien", 48.208, 16.373, None), ("Straßburg", 48.573, 7.752, None),
 ("Innsbruck", 47.269, 11.404, None), ("Luxemburg", 49.611, 6.130, None), ("Nordsee", 54.5, 7.0, None),
]
ROUTE = [  # Ort, lat, lon, erwartete Region, erwartetes "bald"
 ("München", 48.137, 11.575, "by", None), ("Aschaffenburg", 49.974, 9.150, "by", None), ("Frankfurt", 50.111, 8.682, "west", "rm"), ("Darmstadt", 49.873, 8.651, "west", "rm"),
 ("Mainz", 49.993, 8.247, "west", "rm"), ("Wiesbaden", 50.083, 8.240, "west", "rm"), ("Kassel", 51.313, 9.479, "west", None), ("Köln", 50.938, 6.960, "west", None),
 ("Koblenz", 50.357, 7.589, "west", None), ("Stuttgart", 48.776, 9.183, None, None), ("Berlin", 52.520, 13.405, None, None), ("Zürich", 47.377, 8.540, None, None),
 ("Gießen", 50.584, 8.678, "west", "rm"), ("Fulda", 50.555, 9.680, "west", None),
]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page()
        await pg.goto("http://localhost:8765/"); await pg.wait_for_timeout(400)
        bad = 0
        for name, lat, lon, exp in CASES:
            got = await pg.evaluate("([a,b]) => window.__tank.stateAt(a,b)", [lat, lon])
            if got != exp: bad += 1; print("FALSCH", name, "erwartet", exp, "bekommen", got)
        for name, lat, lon, reg, soon in ROUTE:
            f = await pg.evaluate("([a,b]) => window.__tank.resolveFix(a,b,10)", [lat, lon])
            if f["region"] != reg or f["soon"] != soon: bad += 1; print("FALSCH Route", name, "erwartet", reg, soon, "bekommen", f["region"], f["soon"])
        # Lücken und Überlappungen: Zufallspunkte in Deutschland
        res = await pg.evaluate("""() => { let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647; const cnt = {}; let t0 = performance.now();
          for (let i = 0; i < 20000; i++) { const lat = 47.3 + rnd() * 7.6, lon = 5.9 + rnd() * 9.1; const c = window.__tank.stateAt(lat, lon) || 'außen'; cnt[c] = (cnt[c] || 0) + 1; }
          return { cnt, ms: Math.round(performance.now() - t0) }; }""")
        total_in = sum(v for k, v in res["cnt"].items() if k != "außen")
        print("Fälle:", len(CASES) + len(ROUTE), "| falsch:", bad, "| 20000 Zufallspunkte in", res["ms"], "ms | Anteil BY: %.1f %% (Fläche real 19,7 %%)" % (100 * res["cnt"].get("BY", 0) / total_in))
        await b.close()
        sys.exit(1 if bad else 0)
asyncio.run(main())
