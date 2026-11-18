# Quelltexte der Websites falschtanknotdienst.de und tankdoktor.de

Dieser Zweig enthält die Quelltexte. Die veröffentlichten Seiten liegen jeweils im Zweig `main` der Repositorys
`falschtanknotdienst-de` und `tankdoktor-de` und werden über GitHub Pages ausgeliefert.

## Aufbau
- `src/` – Vorlage (`index.html`), Gestaltung (`style.css`), Texte Englisch/Türkisch und Chat (`strings.js`), Verhalten und Chatbot (`app.js`), Fehlerseite (`404.html`), Admin-Bereich (`admin.html`), Farbthemen (`themes.json`), Karte (`map.svg`). Deutsch steht direkt in `index.html`.
- `src/lang/` – Sprachpakete, die erst bei Bedarf geladen werden.
- `config.json` – gemeinsame Angaben: Telefonnummern, Preise, Firma, Bewertungslinks und Bewertungszahlen (`reviewCounts`).
- `sites/*.json` – Angaben je Domain: Name, Schriftzug, Titel, Hauptadresse (`canonical`), Bildzeichen (`mark`), Farbthema der Logo-Dateien (`logoTheme`).
- `assets/fonts/` – Schriften (Sofia Sans, Sofia Sans Condensed, SIL Open Font License) für Latein, Kyrillisch und Griechisch.
- `assets/brand/<name>/<thema>/` – App-Symbole und Teilen-Bild je Website und Farbthema (erzeugt von `tools/brand.py`).
- `logo/<name>/` – Logo-Dateien als SVG und PNG samt Übersicht.
- `tools/` – Build- und Prüfskripte.

## Ändern und veröffentlichen
1. Text oder Angabe in `src/`, `config.json` oder `sites/` ändern.
2. Den Stand von GitHub holen (der Admin-Bereich lädt selbst Änderungen hoch) und `theme.txt` der Website in den Ausgabeordner legen.
3. Beide Seiten bauen: `python3 tools/build.py site sites/tankdoktor.json <ordner>/tankdoktor.de` und ebenso für `falschtanknotdienst`.
4. Prüfen (siehe unten), dann den Inhalt des Ausgabeordners in den Zweig `main` des passenden Repositorys legen, committen, pushen.

## Logo und Bildzeichen
- `tools/marks.py` hält die Bildzeichen: `zapf` (Zapfpistole mit Rückpfeil, falschtanknotdienst.de) und `puls` (Tropfen mit Pulslinie, tankdoktor.de). Welche Website welches Zeichen zeigt, steht in `sites/*.json` unter `mark`.
- `tools/zeichen.py` berechnet den Pfad für `puls` (Tropfen minus Pulslinie, ein einziger Pfad).
- `python3 tools/brand.py` erzeugt für jede Website die Logo-Dateien (`logo/<name>/`), App-Symbole und Teilen-Bilder für alle Farbthemen (`assets/brand/`). Braucht `fontTools`, `brotli`, `uharfbuzz`, `skia-pathops` (nur für `zeichen.py`), Playwright mit Chrome und die Schriftquellen unter `fonts-src/` (`npm install @fontsource-variable/sofia-sans @fontsource-variable/sofia-sans-condensed`).
- Auf der Seite folgt das Zeichen dem Farbthema. Symbol im Browser-Tab, App-Symbol, Teilen-Bild und Manifest liegen für jedes Thema unter `brand/<thema>/`; der Admin-Bereich stellt beim Themenwechsel die Verweise in `index.html` mit um (ein einziger Schritt, keine weiteren Dateien).

## Standort-Weiche und Karte
- `assets/geo/de-states-ne10m.geojson`: Grenzen der 16 Bundesländer aus Natural Earth 1:10m (gemeinfrei).
- `python3 -I tools/geo.py` erzeugt daraus `src/geo.js` (vereinfacht, gemeinsame Grenzen bleiben lückenlos).
- `python3 -I tools/karte.py` erzeugt `src/map.svg`, die kleine Karte im Abschnitt „Hier sind wir im Einsatz“. Die Zonen (Rhein-Main, Heidelberg/Mannheim) kommen aus `config.json` → `soon`.

## Sprachen
- 14 Sprachen: Deutsch (im HTML), Englisch und Türkisch (`src/strings.js`), dazu als Pakete in `src/lang/`: Arabisch, Russisch, Ukrainisch, Polnisch, Rumänisch, Spanisch, Bulgarisch, Französisch, Italienisch, Albanisch, Griechisch.
- `node tools/check_lang.js` prüft alle Pakete gegen die englische Vorlage (Schlüssel, Platzhalter, HTML-Tags).
- Neue Sprache: Paket in `src/lang/` anlegen, Kürzel in `LANGS`, den deutschen Namen in `LANG_DE` und Ja/Nein in `YESNO` eintragen (alle in `src/app.js`), Knopf und Flagge in `src/index.html` ergänzen (Kopfzeile und Fuß), Kürzel in den `:lang()`-Regeln von `src/style.css` und in `tools/check_layout.py` aufnehmen.
- `python3 tools/fontfix.py` erzeugt die kyrillischen Schnitte mit internationalen Buchstabenformen (nötig für Ukrainisch) und die griechischen Schnitte.
- Die Zahl der Bewertungen in der Fakten-Leiste (`{{REVIEWS_TOTAL}}`) ist die Summe aus `reviewCounts`. Ändert sich die Zahl, in den slawischen Sprachen, im Rumänischen und im Arabischen die Wortform prüfen.

## Prüfen
Server: Ausgabeordner auf Port 8766, `dist/` (Vorschau: `python3 tools/build.py preview sites/tankdoktor.json`) auf Port 8765.
- `python3 tools/check_layout.py tankdoktor.de falschtanknotdienst.de` – Breiten, Sprachen, Standort-Zustände.
- `python3 tools/device_test.py tankdoktor.de` – Android- und iPhone-Profile.
- `python3 tools/nlu_test.py` – Sprachverständnis des Chats.
- `python3 -I tools/geo_test.py` – Standort-Erkennung.
