#!/usr/bin/env python3
"""Kyrillische Schnitte von Sofia Sans: internationale Buchstabenformen als Standard.
   Die Schrift zeigt Kyrillisch von Haus aus in bulgarischen Formen und schaltet nur für Russisch (RUS, Merkmal locl) um.
   Ukrainisch bekäme sonst bulgarische Formen. Hier wird das locl-Merkmal zum Standard der kyrillischen Schrift.
   Quelle: @fontsource-variable (SIL Open Font License 1.1). Aufruf: python3 tools/fontfix.py"""
import pathlib, shutil
from fontTools.ttLib import TTFont
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "fonts-src/node_modules/@fontsource-variable"
JOBS = [("sofia-sans/files/sofia-sans-cyrillic-wght-normal.woff2", "ss-cyrillic.woff2"),
        ("sofia-sans-condensed/files/sofia-sans-condensed-cyrillic-wght-normal.woff2", "ssc-cyrillic.woff2")]
for src, dst in JOBS:
    f = TTFont(SRC / src)
    gsub = f["GSUB"].table
    for sr in gsub.ScriptList.ScriptRecord:
        if sr.ScriptTag != "cyrl":
            continue
        rus = [ls.LangSys for ls in sr.Script.LangSysRecord if ls.LangSysTag.strip() == "RUS"][0]
        d = sr.Script.DefaultLangSys
        d.FeatureIndex = sorted(set(d.FeatureIndex) | set(rus.FeatureIndex))
        d.FeatureCount = len(d.FeatureIndex)
    f.flavor = "woff2"
    f.save(ROOT / "assets/fonts" / dst)
    print(dst, (ROOT / "assets/fonts" / dst).stat().st_size, "Bytes")
lic = SRC / "sofia-sans/LICENSE"
if lic.exists():
    shutil.copy2(lic, ROOT / "assets/fonts/LICENSE.txt"); print("Lizenz kopiert:", lic.stat().st_size, "Bytes")
