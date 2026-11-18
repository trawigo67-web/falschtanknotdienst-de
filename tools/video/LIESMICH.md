# Erklärvideo „Falsch getankt? Das tun Sie jetzt."

Vorlage der Animation: `anim.html` + `anim.js`. `render.py` nimmt sie Bild für Bild mit Playwright auf (30 fps) und gibt sie an ffmpeg.

Schalter in der Adresse: `lang=de|tr`, `fmt=v` (hochkant 1080×1920, sonst quer 1920×1080), `brand=nd|td`
(falschtanknotdienst.de oder tankdoktor.de), `end=<Sekunden>` (Gesamtlänge, wenn der Schlusssatz anders lang ist).

Aufruf: `python3 render.py "lang=de&fmt=v" 0 2 teil1.mp4` und `... 1 2 teil2.mp4`, dann mit ffmpeg zusammenfügen und den Ton unterlegen.
Die Pfade in `anim.html` (Schrift) und `render.py` (Vorlage) zeigen auf die Arbeitsumgebung und müssen angepasst werden.

Die Szenenzeiten (`B` in `anim.js`) stammen aus den Sprechpausen der ElevenLabs-Aufnahmen
(Deutsch: Felix Serenitas, Türkisch: Ahmet Akyalçın, Modell eleven_v4). Die Tonspuren liegen nicht im Repository.

Die fertigen Web-Fassungen liegen unter `assets/video/<name>/` (de-h, de-v, tr-h, tr-v als mp4 und jpg).
