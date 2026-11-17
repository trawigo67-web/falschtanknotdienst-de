import asyncio, json
from playwright.async_api import async_playwright
CASES = [
 ("Ich habe Benzin in meinen Diesel getankt", {"kase":"p_in_d"}),
 ("benzin statt diesel getankt und 2 km gefahren", {"kase":"p_in_d","engine":"yes"}),
 ("Diesel statt Benzin getankt, Motor ist aus", {"kase":"d_in_p","engine":"no"}),
 ("hab diesel in den benziner gekippt, noch nicht gestartet", {"kase":"d_in_p","engine":"no"}),
 ("In meinen Diesel habe ich versehentlich Super getankt", {"kase":"p_in_d"}),
 ("in meinen Benziner Diesel getankt", {"kase":"d_in_p"}),
 ("Super E10 im Diesel, stehe in Köln an der Aral", {"kase":"p_in_d","state":"nrw"}),
 ("AdBlue in den Dieseltank gefüllt", {"kase":"adblue"}),
 ("Diesel in den AdBlue Tank getankt", {"kase":"inadblue"}),
 ("adblue falsch getankt", {"ambig":True}),
 ("E10 statt E5 getankt", {"kase":"grade"}),
 ("Super statt Super Plus", {"kase":"grade"}),
 ("Mein Wohnmobil steht in München, Benzin im Diesel, nur Zündung war an", {"kase":"p_in_d","vehicle":"camper","state":"by","engine":"ign"}),
 ("Was kostet das?", {"intent":"price"}),
 ("Wie schnell seid ihr da?", {"intent":"time"}),
 ("zahlt das die versicherung", {"intent":"ins"}),
 ("kann ich noch weiterfahren?", {"intent":"drive"}),
 ("Kann ich mit Karte zahlen?", {"intent":"pay"}),
 ("kommt ihr auch nach 50667", {"state":"nrw"}),
 ("ich stehe in 80331", {"state":"by"}),
 ("Frankfurt", {"state":"he"}),
 ("I put petrol in my diesel car and drove 5 km", {"kase":"p_in_d","engine":"yes"}),
 ("diesel in a petrol car, engine is off", {"kase":"d_in_p","engine":"no"}),
 ("how much does it cost", {"intent":"price"}),
 ("Dizel araca benzin koydum, motoru çalıştırmadım", {"kase":"p_in_d","engine":"no"}),
 ("benzinli araca mazot doldurdum ve sürdüm", {"kase":"d_in_p","engine":"yes"}),
 ("dizel yerine benzin aldım", {"kase":"p_in_d"}),
 ("benzin yerine dizel aldım, Münih'teyim", {"kase":"d_in_p","state":"by"}),
 ("ne kadar tutar", {"intent":"price"}),
 ("hallo", {"greet":True}),
 ("danke", {"thanks":True}),
 ("Transporter in Mainz", {"vehicle":"van","state":"rp"}),
 ("mein auto steht in aschaffenburg", {"vehicle":"car","state":"by"}),
 ("was soll ich jetzt machen", {}),
]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page(); await pg.goto("http://localhost:8765/index.html")
        bad = 0
        for text, exp in CASES:
            u = await pg.evaluate("t => window.__tank.understand(t)", text)
            ok = all(u.get(k) == v for k, v in exp.items())
            if not exp: ok = not u["kase"] and not u["intent"] and not u["engine"]
            if not ok: bad += 1; print("FAIL", text, "->", {k: u[k] for k in ("kase","ambig","engine","vehicle","state","intent")}, "erwartet", exp)
        print("NLU:", len(CASES) - bad, "von", len(CASES), "richtig")
        await b.close()
asyncio.run(main())
