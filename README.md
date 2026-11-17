# Quelltexte der Websites falschtanknotdienst.de und tankdoktor.de

Dieser Zweig enthält die Quelltexte. Die veröffentlichten Seiten liegen jeweils im Zweig `main` der Repositorys
`falschtanknotdienst-de` und `tankdoktor-de` und werden über GitHub Pages ausgeliefert.

## Aufbau
- `src/` – Vorlage (`index.html`), Gestaltung (`style.css`), Texte Englisch/Türkisch und Chat (`strings.js`), Verhalten und Chatbot (`app.js`), Fehlerseite (`404.html`). Deutsch steht direkt in `index.html`.
- `config.json` – gemeinsame Angaben: Telefonnummern, Preise, Firma, Bewertungslinks.
- `sites/*.json` – Angaben je Domain: Name, Schriftzug, Titel, Hauptadresse (`canonical`).
- `assets/` – Schriften (Sofia Sans, Sofia Sans Condensed, SIL Open Font License) und App-Symbole.
- `logo/` – Bildzeichen und Schriftzüge als SVG und PNG.
- `tools/build.py` – baut eine Website: `python3 tools/build.py site sites/tankdoktor.json out/tankdoktor.de`
- `tools/brand.py` – erzeugt Schriftzüge und Vorschaubild (`og.png`); braucht zusätzlich die Schriftdatei aus dem npm-Paket `@fontsource-variable/sofia-sans-condensed` unter `fonts-src/`.
- `tools/overflow2.py`, `tools/nlu_test.py` – Prüfungen (Bildschirmbreiten, Sprachverständnis des Chatbots).

## Ändern und veröffentlichen
1. Text oder Angabe in `src/` oder `config.json` ändern.
2. Beide Seiten bauen (siehe oben).
3. Inhalt von `out/<domain>/` in den Zweig `main` des passenden Repositorys kopieren, committen, pushen.

## Standort-Weiche (seit 17.11.2026)
- `assets/geo/de-states-ne10m.geojson`: Grenzen der 16 Bundesländer aus Natural Earth 1:10m (gemeinfrei).
- `python3 -I tools/geo.py` erzeugt daraus `src/geo.js` (vereinfacht, gemeinsame Grenzen bleiben lückenlos).
- `config.json` → `soon.rm`: Region Rhein-Main als „Bald“ (Mittelpunkt Frankfurt, Radius 60 km). Wenn die eigene Nummer da ist, wird daraus ein drittes Gebiet.
- Tests: `tools/geo_test.py` (90 Orte), `tools/check_layout.py` (Breiten, Sprachen, Standort-Zustände), `tools/device_test.py` (Android- und iPhone-Profile), `tools/nlu_test.py` (Chat).
