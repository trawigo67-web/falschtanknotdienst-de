"""Unterseiten für die Google-Suche: Ratgeber zu den Fällen, Kosten und die drei Einsatzgebiete.

Jede Seite ist eine eigene Adresse mit eigenem Titel, eigener Beschreibung und echtem Inhalt, der ohne JavaScript
lesbar ist. Die Einsatzgebiete entsprechen den drei Teams mit eigener Nummer (keine Städteseiten nur mit
ausgetauschtem Ortsnamen: Google wertet das als Brückenseiten).
Fakten zu Sofortmaßnahmen, Fällen und Versicherung: ADAC-Ratgeber „Falsch getankt?“ (Stand November 2026).
"""
import html as htmlmod
import json

E = htmlmod.escape


def call_box(cfg, only=None):
    rows = []
    for key, label in (("west", "NRW, Hessen, Rheinland-Pfalz"), ("rm", "Frankfurt und Rhein-Main"), ("by", "Bayern")):
        if only and key not in only:
            continue
        r = cfg["regions"][key]
        rows.append('<a class="pg-call" href="tel:%s"><span class="pg-call-l">Jetzt anrufen</span><span class="pg-call-n">%s</span>'
                    '<span class="pg-call-w">%s</span></a>' % (r["tel"], E(r["num"]), E(label)))
    return '<div class="pg-calls">%s</div>' % "".join(rows)


def pages(cfg):
    car, camper = cfg["price"]["car"], cfg["price"]["camper"]
    W, R, B = (cfg["regions"][k]["num"] for k in ("west", "rm", "by"))
    first = """<div class="pg-alert"><strong>Motor aus lassen.</strong> Nicht starten, die Zündung nicht einschalten. Sind Sie schon gefahren:
an der nächsten sicheren Stelle anhalten, Motor abstellen, nicht erneut starten.</div>"""
    P = []

    P.append(dict(slug="falsch-getankt", short="Falsch getankt: was tun?",
        title="Falsch getankt? Was Sie jetzt tun sollten | {brand}",
        desc="Falsch getankt: Motor aus lassen, Zündung aus, Tank abpumpen lassen. Was bei Benzin im Diesel, Diesel im Benziner und AdBlue gilt.",
        h1="Falsch getankt: was Sie jetzt tun sollten",
        lead="Wer an der Zapfsäule den falschen Kraftstoff erwischt, kann den Schaden meist klein halten. Entscheidend ist, was in den nächsten Minuten passiert.",
        body=first + """
<h2>Die ersten Schritte</h2>
<ol>
<li><strong>Tankvorgang sofort stoppen.</strong> Je weniger falscher Kraftstoff im Tank ist, desto besser.</li>
<li><strong>Motor nicht starten, Zündung aus lassen.</strong> Bei manchen Autos läuft die Kraftstoffpumpe schon an, wenn die Fahrertür geöffnet oder die Zündung eingeschaltet wird. Dann gelangt das Gemisch aus dem Tank in die Leitungen.</li>
<li><strong>Schon losgefahren?</strong> Anhalten, sobald es sicher geht, Motor abstellen und nicht erneut starten.</li>
<li><strong>Fahrzeug nicht selbst leeren.</strong> Kraftstoff ist leicht entzündlich und muss fachgerecht entsorgt werden.</li>
<li><strong>Anrufen.</strong> Wir sagen Ihnen am Telefon den Preis und wann wir da sind, und pumpen den Tank direkt vor Ort ab.</li>
</ol>
<h2>Welcher Fall liegt vor?</h2>
<ul class="pg-cards">
<li><a href="/benzin-im-diesel/"><strong>Benzin im Diesel</strong><span>Der häufigste und heikelste Fall.</span></a></li>
<li><a href="/diesel-im-benziner/"><strong>Diesel im Benziner</strong><span>Seltener, weil der Stutzen meist kleiner ist.</span></a></li>
<li><a href="/adblue-im-dieseltank/"><strong>AdBlue im Dieseltank</strong><span>Zündung aus lassen ist hier besonders wichtig.</span></a></li>
<li><a href="/motorrad/"><strong>Motorrad</strong><span>Diesel im Benziner, E10 ohne Freigabe.</span></a></li>
<li><a href="/transporter-lkw/"><strong>Transporter und Lkw</strong><span>Auch große Tanks, auch AdBlue.</span></a></li>
</ul>
<h2>Was nicht so schlimm ist</h2>
<p><strong>Super Plus statt Super</strong> ist unkritisch, Sie haben nur mehr bezahlt. <strong>E10 statt E5</strong> ist unbedenklich, wenn Ihr Auto für E10 freigegeben ist; das steht in den Herstellerangaben. Ist es nicht freigegeben, tanken Sie möglichst bald ethanolarmen Kraftstoff nach und fragen Sie im Zweifel kurz bei uns nach.</p>
<h2>Woran Sie den richtigen Kraftstoff erkennen</h2>
<p>An der Form des Zeichens auf Zapfpistole und Tankklappe: Ein <strong>Kreis</strong> steht für Benzin (E5, E10), ein <strong>Quadrat</strong> für Diesel (B7). AdBlue gehört nur in den eigenen Einfüllstutzen, meist mit blauem Deckel.</p>
<h2>Wer die Kosten trägt</h2>
<p>In der Regel zahlt der Fahrer selbst; die Kfz-Haftpflicht springt meist nicht ein. Manche Schutzbriefe übernehmen einen Teil. Mehr dazu: <a href="/versicherung/">Zahlt die Versicherung?</a> und <a href="/kosten/">Was das Abpumpen kostet</a>.</p>
"""))

    P.append(dict(slug="benzin-im-diesel", short="Benzin im Diesel",
        title="Benzin im Diesel getankt? Was jetzt zu tun ist | {brand}",
        desc="Benzin statt Diesel getankt: Warum schon wenig Benzin moderne Diesel schädigen kann, was Sie jetzt tun und wie das Abpumpen vor Ort abläuft.",
        h1="Benzin im Diesel getankt",
        lead="Der häufigste Fall an der Zapfsäule: Die Benzinpistole passt problemlos in den Dieselstutzen. Für moderne Dieselmotoren ist das ernst.",
        body=first + """
<h2>Warum Benzin dem Diesel schadet</h2>
<p>Dieselkraftstoff schmiert die Hochdruckpumpe und die Einspritzdüsen mit. Benzin tut das nicht. Läuft der Motor mit dem Gemisch, kann das Einspritzsystem Schaden nehmen. Dann müssen im schlimmsten Fall Hochdruckpumpe, Injektoren, Leitungen und Tank getauscht werden, was mehrere tausend Euro kosten kann.</p>
<p>Dass ein paar Liter Benzin im Diesel nichts ausmachen, galt für alte Vorkammer- und Wirbelkammer-Diesel. Bei heutigen Motoren mit Common-Rail- oder Pumpe-Düse-Einspritzung stimmt das nicht mehr.</p>
<h2>Solange der Motor nicht gelaufen ist</h2>
<p>Dann ist das Gemisch nur im Tank. Der Tank wird abgepumpt, das System gespült, und Sie tanken richtigen Diesel. In aller Regel können Sie danach weiterfahren.</p>
<h2>Wenn Sie schon gefahren sind</h2>
<p>Anhalten, Motor aus, nicht erneut starten. Sagen Sie uns am Telefon, wie weit Sie gefahren sind und ob der Motor unruhig lief. Oft reichen auch dann Abpumpen und Spülen. Ob zusätzlich eine Werkstatt nötig ist, sagen wir Ihnen ehrlich.</p>
<h2>So läuft der Einsatz</h2>
<ol>
<li>Sie rufen an und sagen, wo Sie stehen, welches Auto und wie viel getankt wurde.</li>
<li>Sie erfahren den Festpreis, bevor wir losfahren.</li>
<li>Wir pumpen das Gemisch vor Ort ab, spülen und füllen richtigen Kraftstoff auf.</li>
<li>Den abgepumpten Kraftstoff nehmen wir zur fachgerechten Entsorgung mit.</li>
</ol>
<p>Andere Fälle: <a href="/diesel-im-benziner/">Diesel im Benziner</a> · <a href="/adblue-im-dieseltank/">AdBlue im Dieseltank</a> · <a href="/falsch-getankt/">alle Sofortmaßnahmen</a></p>
"""))

    P.append(dict(slug="diesel-im-benziner", short="Diesel im Benziner",
        title="Diesel im Benziner getankt? Was jetzt zu tun ist | {brand}",
        desc="Diesel statt Benzin getankt: Motor aus lassen, Menge prüfen, Tank abpumpen lassen. Was Diesel im Benzinmotor anrichtet und wie wir vor Ort helfen.",
        h1="Diesel im Benziner getankt",
        lead="Seltener als der umgekehrte Fall, weil die Dieselpistole bei vielen Autos nicht in den Benzinstutzen passt. Bei aktuellen Modellen klappt es trotzdem oft.",
        body=first + """
<h2>Was Diesel im Benzinmotor anrichtet</h2>
<p>Diesel zündet im Benzinmotor schlecht. Der Motor läuft unrund, ruckelt oder geht aus. Schäden an der Einspritzanlage und an der Abgasreinigung, etwa am Katalysator, sind nicht auszuschließen.</p>
<h2>Kommt es auf die Menge an?</h2>
<p>Ja. Wenige Liter Diesel in einem fast vollen Benzintank sind weniger kritisch als ein halb voller Tank Diesel. Was für Ihr Auto gilt, steht in der Betriebsanleitung. Im Zweifel: Motor aus lassen und anrufen. Am Telefon klären wir mit Ihnen, ob Abpumpen nötig ist.</p>
<h2>So helfen wir</h2>
<p>Wir pumpen den Tank vor Ort ab, spülen das Kraftstoffsystem und füllen richtigen Kraftstoff auf. Ohne Abschleppen und ohne Werkstatttermin. Den Festpreis nennen wir Ihnen vorab am Telefon.</p>
<p>Andere Fälle: <a href="/benzin-im-diesel/">Benzin im Diesel</a> · <a href="/adblue-im-dieseltank/">AdBlue im Dieseltank</a> · <a href="/falsch-getankt/">alle Sofortmaßnahmen</a></p>
"""))

    P.append(dict(slug="adblue-im-dieseltank", short="AdBlue im Dieseltank",
        title="AdBlue im Dieseltank? Zündung aus lassen | {brand}",
        desc="AdBlue versehentlich in den Dieseltank gefüllt: Warum die Zündung aus bleiben muss, was eine Tankreinigung bringt und wie wir vor Ort helfen.",
        h1="AdBlue im Dieseltank",
        lead="AdBlue ist eine Harnstofflösung für die Abgasreinigung. Im Dieseltank hat sie nichts verloren, und hier zählt besonders, dass die Zündung aus bleibt.",
        body=first + """
<h2>Warum die Zündung aus bleiben muss</h2>
<p>Solange die Zündung nicht eingeschaltet war, ist das AdBlue nur im Tank. Dann genügt meist eine gründliche Reinigung des Tanks. Wird die Zündung eingeschaltet, kann die Kraftstoffpumpe AdBlue in das Einspritzsystem befördern. Dann müssen oft Pumpen, Leitungen, Filter und Injektoren erneuert werden.</p>
<h2>Der umgekehrte Fall</h2>
<p>Diesel oder Benzin im AdBlue-Tank ist kaum möglich: Der AdBlue-Stutzen ist mit 19,75 Millimetern enger als die Zapfpistolen für Diesel (25 Millimeter) und Benzin (21 Millimeter).</p>
<h2>So helfen wir</h2>
<p>Wir pumpen den Tank vor Ort ab und reinigen ihn, bevor richtiger Diesel hineinkommt. Sagen Sie uns am Telefon, ob die Zündung eingeschaltet war. Dann sagen wir Ihnen ehrlich, ob zusätzlich eine Werkstatt nötig ist.</p>
<p>Andere Fälle: <a href="/benzin-im-diesel/">Benzin im Diesel</a> · <a href="/diesel-im-benziner/">Diesel im Benziner</a> · <a href="/falsch-getankt/">alle Sofortmaßnahmen</a></p>
"""))

    P.append(dict(slug="kosten", short="Kosten",
        title="Abpumpen nach Falschbetankung: Kosten | {brand}",
        desc="Abpumpen nach Falschbetankung: Pkw ab %s €, Wohnmobil ab %s €. Festpreis am Telefon, bevor wir losfahren. Wer die Kosten trägt und wie Sie bezahlen." % (car, camper),
        h1="Was das Abpumpen kostet",
        lead="Sie erfahren den Preis am Telefon, bevor wir losfahren. Erst wenn Sie zustimmen, kommen wir.",
        body="""
<div class="pg-prices"><div><span>Pkw</span><strong>ab %s €</strong><small>Abpumpen und Spülen</small></div><div><span>Wohnmobil</span><strong>ab %s €</strong><small>Größerer Tank, längere Absaugung</small></div></div>
<h2>Wovon der Preis abhängt</h2>
<ul>
<li>Fahrzeug und Tankgröße</li>
<li>wie viel falscher Kraftstoff im Tank ist</li>
<li>ob der Motor schon gelaufen ist und gespült werden muss</li>
<li>wo Sie stehen</li>
</ul>
<p>Transporter, Motorrad oder ein anderes Fahrzeug? Den Preis erfahren Sie ebenfalls direkt am Telefon.</p>
<h2>Wer die Kosten trägt</h2>
<p>Meist der Fahrer selbst: Die Kfz-Versicherung zahlt bei einer Falschbetankung in der Regel nicht. Manche Schutzbriefe und Kaskoverträge übernehmen einen Teil. Sie erhalten von uns eine Rechnung, die Sie einreichen können. Mehr dazu: <a href="/versicherung/">Zahlt die Versicherung?</a></p>
<h2>Warum Abpumpen sich lohnt</h2>
<p>Läuft der Motor mit dem falschen Kraftstoff, kann ein Schaden am Einspritzsystem entstehen, der mehrere tausend Euro kostet. Abpumpen, solange das Gemisch nur im Tank ist, ist dagegen günstig.</p>
<h2>So bezahlen Sie</h2>
<p>Direkt vor Ort: bar, per Echtzeit-Überweisung, mit PayPal oder mit Karte (Visa, Mastercard, American Express, Maestro).</p>
""" % (car, camper)))

    P.append(dict(slug="versicherung", short="Zahlt die Versicherung?",
        title="Falsch getankt: Zahlt die Versicherung? | {brand}",
        desc="Haftpflicht, Teilkasko, Vollkasko, Schutzbrief: wer bei Falschbetankung zahlt, was im Vertrag steht und was Sie für die Versicherung festhalten sollten.",
        h1="Falsch getankt: Zahlt die Versicherung?",
        lead="Meistens nicht. Ganz ausgeschlossen ist es aber nicht. Entscheidend sind Ihr Vertrag und wie es zur Falschbetankung kam.",
        body="""
<h2>Die Versicherungen im Überblick</h2>
<ul>
<li><strong>Kfz-Haftpflicht:</strong> Sie zahlt für Schäden, die Sie anderen zufügen, nicht für Ihr eigenes Auto. Für das Abpumpen oder eine Reparatur am eigenen Fahrzeug ist sie in der Regel nicht zuständig.</li>
<li><strong>Vollkasko:</strong> Viele Bedingungen schließen sogenannte Betriebs- oder Bedienungsschäden aus, und dazu zählt eine Falschbetankung meist. Ein Blick in Ihre Vertragsbedingungen lohnt sich trotzdem.</li>
<li><strong>Teilkasko:</strong> Das Oberlandesgericht Düsseldorf hat 2008 in einem Einzelfall Teilkasko-Schutz für einen Falschbetankungsschaden zugesprochen (Az. I-4 U 12/08). Daraus folgt kein Anspruch für jeden Vertrag; es kommt auf die Bedingungen an.</li>
<li><strong>Schutzbrief und Automobilclub:</strong> Je nach Tarif werden Pannenhilfe oder Abschleppen übernommen. Das Abpumpen selbst oder Schäden am Kraftstoffsystem sind damit nicht automatisch abgedeckt. Fragen Sie im Zweifel kurz bei Ihrem Anbieter nach.</li>
</ul>
<h2>Wenn die Tankstelle schuld sein könnte</h2>
<p>Hat Tankstellenpersonal falsch getankt oder war die Zapfsäule falsch beschriftet, kann die Tankstelle haften. Das hängt vom Einzelfall und vom Nachweis ab. Machen Sie deshalb sofort Fotos von Zapfsäule, Zapfpistole und Beschilderung, heben Sie den Kassenbon auf und notieren Sie Zeugen.</p>
<h2>Was Sie für die Versicherung festhalten sollten</h2>
<ol>
<li>Kassenbon mit Kraftstoffsorte und Menge</li>
<li>Fotos von Zapfsäule und Tankklappe</li>
<li>ob der Motor gelaufen ist und wie weit Sie gefahren sind</li>
<li>unsere Rechnung über das Abpumpen</li>
</ol>
<p>Wir sind kein Versicherungsberater. Was Ihr Vertrag abdeckt, kann nur Ihre Versicherung verbindlich sagen.</p>
<p>Mehr dazu: <a href="/kosten/">Was das Abpumpen kostet</a> · <a href="/falsch-getankt/">Was Sie jetzt tun sollten</a></p>
"""))

    P.append(dict(slug="mietwagen-firmenwagen", short="Mietwagen, Leasing, Firmenwagen",
        title="Mietwagen oder Firmenwagen falsch getankt? | {brand}",
        desc="Falsch getankt mit Mietwagen, Leasing- oder Firmenwagen: zuerst Vermieter oder Arbeitgeber anrufen, Motor aus lassen, alles festhalten. So helfen wir danach.",
        h1="Falsch getankt mit Mietwagen, Leasing- oder Firmenwagen",
        lead="Das Auto gehört nicht Ihnen. Deshalb gilt neben „Motor aus lassen“ vor allem eins: zuerst den Eigentümer anrufen.",
        body=first + """
<h2>So gehen Sie vor</h2>
<ol>
<li><strong>Motor aus lassen</strong>, Zündung nicht einschalten.</li>
<li><strong>Vermieter, Leasinggeber oder Arbeitgeber anrufen.</strong> Viele Vermieter haben eine eigene Pannennummer und schreiben vor, wer das Auto abpumpen darf. Wer ohne Zustimmung selbst einen Dienst beauftragt, verstößt womöglich gegen die Mietbedingungen.</li>
<li><strong>Alles festhalten:</strong> Kassenbon, Fotos von Zapfsäule und Tankklappe, Uhrzeit, ob der Motor gelaufen ist.</li>
<li><strong>Erst dann uns beauftragen</strong>, wenn der Vermieter oder Ihr Fuhrpark zustimmt oder Sie selbst entscheiden dürfen.</li>
</ol>
<h2>Wer zahlt?</h2>
<p>Bei einem Mietwagen haftet in der Regel, wer den falschen Kraftstoff getankt hat. Typische Mietbedingungen verpflichten dazu, den richtigen Kraftstoff zu verwenden; eine vereinbarte Haftungsreduzierung kann bei Falschbetankung entfallen. Was genau gilt, steht in Ihrem Mietvertrag. Bei Leasing- und Firmenwagen regeln das der Leasingvertrag oder die Firmenwagenregelung.</p>
<h2>So helfen wir</h2>
<p>Wenn Sie uns beauftragen dürfen, pumpen wir vor Ort ab, spülen und füllen richtigen Kraftstoff auf. Sie bekommen eine Rechnung mit allen Angaben, die Vermieter oder Fuhrpark brauchen. Auf Wunsch sprechen wir vorher am Telefon direkt mit Ihrem Fuhrpark.</p>
<p>Mehr dazu: <a href="/versicherung/">Zahlt die Versicherung?</a> · <a href="/kosten/">Kosten</a></p>
"""))

    P.append(dict(slug="motorrad", short="Motorrad falsch getankt",
        title="Motorrad falsch getankt? Abpumpen vor Ort | {brand}",
        desc="Motorrad falsch getankt, etwa Diesel im Benziner oder E10 ohne Freigabe: Motor aus lassen, nicht weiterfahren. Wir pumpen den Tank vor Ort ab.",
        h1="Motorrad falsch getankt",
        lead="Auch am Motorrad passiert es: An vielen Tankstellen passt die Dieselpistole in den Tankstutzen. Dann gilt dasselbe wie beim Auto.",
        body=first + """
<h2>Was jetzt wichtig ist</h2>
<ul>
<li><strong>Nicht starten.</strong> Motorräder fahren mit Benzin; Diesel verbrennt im Benzinmotor schlecht, der Motor läuft unrund oder geht aus.</li>
<li><strong>Nicht selbst ablassen.</strong> Benzin ist leicht entzündlich und muss fachgerecht entsorgt werden.</li>
<li><strong>E10 statt Super?</strong> Unbedenklich, wenn Ihr Motorrad für E10 freigegeben ist. Das steht in den Herstellerangaben. Im Zweifel fragen Sie kurz bei uns nach.</li>
</ul>
<h2>So helfen wir</h2>
<p>Wir kommen zu Ihnen, pumpen den Tank ab, spülen bei Bedarf und füllen richtigen Kraftstoff auf. Sagen Sie uns am Telefon Marke, Modell und wie viel getankt wurde. Den Preis erfahren Sie, bevor wir losfahren.</p>
<p>Mehr dazu: <a href="/diesel-im-benziner/">Diesel im Benziner</a> · <a href="/falsch-getankt/">alle Sofortmaßnahmen</a></p>
"""))

    P.append(dict(slug="transporter-lkw", short="Transporter und Lkw",
        title="Transporter oder Lkw falsch getankt? Abpumpen vor Ort | {brand}",
        desc="Transporter, Lkw oder Bus falsch getankt, auch AdBlue im Dieseltank: Wir pumpen auch große Tanks vor Ort ab, rund um die Uhr. Preis vorab am Telefon.",
        h1="Transporter oder Lkw falsch getankt",
        lead="Bei Nutzfahrzeugen zählt jede Stunde Standzeit. Wir pumpen auch große Tanks direkt vor Ort ab, an der Tankstelle, auf dem Firmenhof oder auf dem Rastplatz.",
        body=first + """
<h2>Typische Fälle</h2>
<ul>
<li><strong>Benzin im Diesel:</strong> Transporter fahren meist mit Diesel. Schon wenig Benzin kann der Einspritzanlage schaden, wenn der Motor läuft. Mehr dazu: <a href="/benzin-im-diesel/">Benzin im Diesel</a>.</li>
<li><strong>AdBlue im Dieseltank:</strong> Bei Lkw liegen Diesel- und AdBlue-Stutzen oft nah beieinander. Zündung aus lassen, dann reicht meist eine gründliche Tankreinigung. Mehr dazu: <a href="/adblue-im-dieseltank/">AdBlue im Dieseltank</a>.</li>
</ul>
<h2>Was wir am Telefon wissen müssen</h2>
<ol>
<li>Fahrzeug und ungefähre Tankgröße</li>
<li>wie viel falscher Kraftstoff getankt wurde</li>
<li>ob der Motor oder die Zündung an war</li>
<li>wo das Fahrzeug steht und ob es dort sicher stehen kann</li>
</ol>
<p>Den Preis erfahren Sie, bevor wir losfahren. Sie bekommen eine Rechnung für Ihre Buchhaltung oder Ihren Fuhrpark.</p>
<p>Mehr dazu: <a href="/mietwagen-firmenwagen/">Firmen- und Leasingfahrzeuge</a> · <a href="/kosten/">Kosten</a></p>
"""))

    regions = [
        dict(key="west", slug="einsatzgebiet/nrw-hessen-rheinland-pfalz", short="NRW, Hessen, Rheinland-Pfalz",
             h1="Falsch getankt in NRW, Hessen oder Rheinland-Pfalz",
             title="Falsch getankt in NRW, Hessen oder RLP? | {brand}",
             desc="Abpumpservice bei Falschbetankung in NRW, Hessen und Rheinland-Pfalz: rund um die Uhr unter %s, Festpreis vorab, direkt vor Ort." % W,
             places="Köln, Düsseldorf, Dortmund, Essen, Duisburg, Bochum, Wuppertal, Bonn, Gelsenkirchen, Mönchengladbach, Aachen, Krefeld, Leverkusen und Solingen sowie die Orte dazwischen, dazu Hessen und Rheinland-Pfalz außerhalb des Rhein-Main-Gebiets.",
             area=["Nordrhein-Westfalen", "Hessen", "Rheinland-Pfalz"],
             note="Für Frankfurt und das Rhein-Main-Gebiet gibt es ein eigenes Team mit eigener Nummer: <a href=\"/einsatzgebiet/frankfurt-rhein-main/\">Rhein-Main</a>."),
        dict(key="rm", slug="einsatzgebiet/frankfurt-rhein-main", short="Frankfurt und Rhein-Main",
             h1="Falsch getankt in Frankfurt und Rhein-Main",
             title="Falsch getankt in Frankfurt/Rhein-Main? | {brand}",
             desc="Abpumpservice bei Falschbetankung in Frankfurt, Offenbach, Darmstadt, Wiesbaden, Mainz und Umgebung: eigenes Team, rund um die Uhr unter %s." % R,
             places="Frankfurt am Main, Offenbach, Darmstadt, Wiesbaden, Mainz, Hanau, Bad Homburg, Rüsselsheim, Friedberg, Gießen, Wetzlar, Limburg, Bensheim und Worms. Dazu der weitere Umkreis bis etwa 100 Kilometer, zum Beispiel Mannheim, Ludwigshafen, Heidelberg, Marburg, Fulda und Koblenz.",
             area=["Frankfurt am Main", "Rhein-Main-Gebiet", "Hessen", "Rheinland-Pfalz"],
             note="Für das Rhein-Main-Gebiet ist ein eigenes Team mit eigener Nummer unterwegs."),
        dict(key="by", slug="einsatzgebiet/bayern", short="Bayern",
             h1="Falsch getankt in Bayern",
             title="Falsch getankt in Bayern? Abpumpen vor Ort | {brand}",
             desc="Abpumpservice bei Falschbetankung in Bayern: München, Nürnberg, Augsburg, Regensburg und entlang der Autobahnen. Rund um die Uhr unter %s." % B,
             places="München, Nürnberg, Augsburg, Regensburg, Ingolstadt, Würzburg, Fürth, Erlangen, Bamberg, Bayreuth, Landshut, Rosenheim, Kempten und Passau. Auch entlang der A3, A8, A9, A93 und A99.",
             area=["Bayern"],
             note="In Bayern fährt unser fester Servicepartner."),
    ]
    for r in regions:
        r.update(lead="Sie stehen mit falschem Kraftstoff im Tank? Lassen Sie den Motor aus und rufen Sie an. Hier erreichen Sie das zuständige Team direkt.",
                 calls=[r["key"]], service_area=r["area"],
                 body=first + """
<h2>Hier sind wir unterwegs</h2>
<p>%s</p>
<p>%s</p>
<h2>So läuft der Einsatz</h2>
<ol>
<li>Sie rufen an und sagen, wo Sie stehen, welches Fahrzeug und welcher Kraftstoff.</li>
<li>Sie erfahren den Festpreis und wann wir bei Ihnen sind, bevor wir losfahren.</li>
<li>Wir pumpen direkt vor Ort ab, an der Tankstelle, auf dem Parkplatz oder vor Ihrer Haustür, spülen und füllen richtigen Kraftstoff auf.</li>
<li>Sie bezahlen vor Ort und bekommen eine Rechnung.</li>
</ol>
<p>Mehr dazu: <a href="/falsch-getankt/">Was Sie jetzt tun sollten</a> · <a href="/kosten/">Kosten</a></p>
""" % (E(r["places"]), r["note"]))
        P.append(r)

    P.append(dict(slug="einsatzgebiet", short="Einsatzgebiet",
        title="Einsatzgebiet: NRW, Hessen, RLP, Bayern | {brand}",
        desc="Drei Teams, drei Nummern: NRW, Hessen und Rheinland-Pfalz; Frankfurt und Rhein-Main; Bayern. Rund um die Uhr Abpumpen bei Falschbetankung.",
        h1="Unser Einsatzgebiet",
        lead="Drei Teams mit eigener Nummer. Rufen Sie das Team an, in dessen Gebiet Sie stehen. In einem anderen Bundesland? Rufen Sie trotzdem an, wir sagen Ihnen sofort, ob wir kommen können.",
        body="""<ul class="pg-cards">
<li><a href="/einsatzgebiet/nrw-hessen-rheinland-pfalz/"><strong>NRW, Hessen, Rheinland-Pfalz</strong><span>%s</span></a></li>
<li><a href="/einsatzgebiet/frankfurt-rhein-main/"><strong>Frankfurt und Rhein-Main</strong><span>%s</span></a></li>
<li><a href="/einsatzgebiet/bayern/"><strong>Bayern</strong><span>%s</span></a></li>
</ul>""" % (E(W), E(R), E(B))))
    return P


CSS = """
.pg{max-width:760px;margin:0 auto;padding:0 20px 120px;font:400 1.0625rem/1.6 var(--font-body);color:var(--ink)}
body{margin:0;background:var(--paper);font-family:var(--font-body);color:var(--ink);-webkit-text-size-adjust:100%}
.pg-top{background:linear-gradient(155deg,var(--sign-hi),var(--sign-lo));color:#fff}
.pg-top-in{max-width:760px;margin:0 auto;padding:14px 20px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.pg-brand{color:#fff;text-decoration:none;font:800 1.25rem/1 var(--font-display);letter-spacing:.01em}
.pg-brand b{color:var(--signal)}
.pg-home{color:#fff;font-size:.9375rem}
.pg-crumbs{font-size:.875rem;color:var(--muted);margin:18px 0 0}
.pg-crumbs a{color:var(--muted)}
.pg h1{font:800 clamp(2rem,6vw,2.75rem)/1.05 var(--font-display);margin:10px 0 12px;letter-spacing:-.005em}
.pg h2{font:800 1.5rem/1.15 var(--font-display);margin:34px 0 10px}
.pg .lead{font-size:1.1875rem;color:var(--muted);margin:0 0 20px}
.pg a{color:var(--link)}
.pg li{margin:6px 0}
.pg-alert{background:var(--surface);border-inline-start:6px solid var(--signal);border-radius:var(--r-s);padding:14px 16px;margin:22px 0;box-shadow:var(--shadow-card)}
.pg-calls{display:grid;gap:10px;margin:18px 0 6px}
.pg-call{display:grid;grid-template-columns:1fr auto;grid-template-areas:"n l" "w l";column-gap:12px;align-items:center;min-height:64px;padding:10px 16px;border-radius:var(--r-btn);
  background:linear-gradient(180deg,var(--signal-hi),var(--signal-lo));color:var(--on-signal)!important;text-decoration:none;box-shadow:var(--shadow-card)}
.pg-call-l{grid-area:l;white-space:nowrap;font-weight:800;font-size:.9375rem;padding:6px 10px;border-radius:999px;background:rgba(0,0,0,.12)}
.pg-call-n{grid-area:n;font:800 1.5rem/1.1 var(--font-display);direction:ltr;white-space:nowrap}
.pg-call-w{grid-area:w;font-size:.875rem;font-weight:600}
.pg-cards{list-style:none;padding:0;display:grid;gap:10px}
.pg-cards a{display:grid;gap:2px;padding:14px 16px;border-radius:var(--r-s);background:var(--surface);border:1px solid var(--line);text-decoration:none;color:var(--ink)}
.pg-cards span{color:var(--muted);font-size:.9375rem}
.pg-prices{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0}
.pg-prices div{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-s);padding:14px 16px;display:grid}
.pg-prices strong{font:800 2rem/1.1 var(--font-display)}
.pg-prices small{color:var(--muted)}
.pg-more{margin-top:40px;padding-top:20px;border-top:1px solid var(--line)}
.pg-more ul{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:8px 16px}
.pg-foot{background:linear-gradient(180deg,var(--foot-a),var(--foot-b));color:#fff;font-size:.9375rem}
.pg-foot .pg-top-in{flex-wrap:wrap}
.pg-foot a{color:#fff}
.pg-sticky{position:fixed;inset-inline:0;bottom:0;padding:10px 14px calc(10px + env(safe-area-inset-bottom));background:var(--surface);box-shadow:0 -8px 24px -12px rgba(0,0,0,.35);display:flex;justify-content:center}
.pg-sticky a{flex:1;max-width:520px;text-align:center;min-height:52px;display:flex;align-items:center;justify-content:center;border-radius:var(--r-btn);
  background:var(--signal);color:var(--on-signal);font-weight:800;text-decoration:none}
a:focus-visible{outline:3px solid var(--focus);outline-offset:3px}
@media (min-width:700px){.pg-calls{grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}.pg-call{grid-template-columns:1fr;grid-template-areas:"l" "n" "w";row-gap:4px;padding:14px 16px}.pg-call-l{justify-self:start}.pg-sticky{display:none}.pg{padding-bottom:60px}}
"""


def render(cfg, p, base_css, theme, url, canon_base, display, brand_html, all_pages, tc=("#FFFFFF", "#000000")):
    path = "/%s/" % p["slug"]
    title = p["title"].format(brand=display)
    canon = canon_base + p["slug"] + "/"
    crumbs = [("Startseite", "/")]
    ld_crumbs = [{"@type": "ListItem", "position": 1, "name": "Startseite", "item": canon_base}]
    if p["slug"].startswith("einsatzgebiet/"):
        crumbs.append(("Einsatzgebiet", "/einsatzgebiet/"))
        ld_crumbs.append({"@type": "ListItem", "position": 2, "name": "Einsatzgebiet", "item": canon_base + "einsatzgebiet/"})
    ld_crumbs.append({"@type": "ListItem", "position": len(ld_crumbs) + 1, "name": p["short"], "item": canon})
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ld_crumbs}]
    if p.get("service_area"):
        r = cfg["regions"][p["key"]]
        ld.append({"@context": "https://schema.org", "@type": "Service", "serviceType": "Abpumpen bei Falschbetankung",
                   "name": p["h1"], "url": canon, "areaServed": p["service_area"],
                   "provider": {"@type": "AutomotiveBusiness", "name": display, "url": canon_base, "telephone": r["tel"]},
                   "availableChannel": {"@type": "ServiceChannel", "servicePhone": {"@type": "ContactPoint", "telephone": r["tel"], "contactType": "emergency"}}})
    else:
        ld.append({"@context": "https://schema.org", "@type": "WebPage", "name": p["h1"], "url": canon, "inLanguage": "de",
                   "publisher": {"@type": "Organization", "name": display, "url": canon_base}})
    crumb_html = " › ".join('<a href="%s">%s</a>' % (h, E(n)) for n, h in crumbs) + " › " + E(p["short"])
    more = "".join('<li><a href="/%s/">%s</a></li>' % (q["slug"], E(q["short"])) for q in all_pages if q["slug"] != p["slug"])
    sticky_tel = cfg["regions"][p["calls"][0]]["tel"] if p.get("calls") else cfg["regions"]["west"]["tel"]
    sticky_num = cfg["regions"][p["calls"][0]]["num"] if p.get("calls") else cfg["regions"]["west"]["num"]
    sticky_lbl = "Jetzt anrufen: %s" % sticky_num if p.get("calls") else "Anrufen (NRW, Hessen, RLP): %s" % sticky_num
    return """<!DOCTYPE html>
<html lang="de" data-theme="%(theme)s">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta name="robots" content="index, follow">
<link rel="canonical" href="%(canon)s">
<meta name="format-detection" content="telephone=no">
<meta name="theme-color" media="(prefers-color-scheme: light)" content="%(tc_light)s">
<meta name="theme-color" media="(prefers-color-scheme: dark)" content="%(tc_dark)s">
<meta property="og:type" content="article">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="%(display)s">
<meta property="og:title" content="%(h1)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(own)s">
<meta property="og:image" content="%(url)sbrand/%(theme)s/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:type" content="image/png">
<meta property="og:image:alt" content="%(display)s: Falsch getankt? Motor aus lassen.">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/brand/%(theme)s/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="96x96" href="/brand/%(theme)s/icon-96.png">
<link rel="icon" type="image/svg+xml" href="/brand/%(theme)s/icon.svg">
<link rel="apple-touch-icon" href="/brand/%(theme)s/icon-180.png">
<link rel="preload" href="/fonts/ssc-latin.woff2" as="font" type="font/woff2" crossorigin>
<style>%(css)s</style>
<script>(function(d){if(!window.fetch||!/^https?:$/.test(location.protocol))return;fetch('/theme.txt',{cache:'no-store'}).then(function(r){return r.ok?r.text():''}).then(function(t){t=t.trim();if(/^[a-z]+$/.test(t)&&t!==d.getAttribute('data-theme')){d.setAttribute('data-theme',t);[].forEach.call(document.querySelectorAll('link[rel~=icon],link[rel=apple-touch-icon]'),function(l){l.href=l.getAttribute('href').replace(/brand\\/[a-z]+\\//,'brand/'+t+'/')})}}).catch(function(){})})(document.documentElement);</script>
<script type="application/ld+json">%(ld)s</script>
</head>
<body>
<header class="pg-top"><div class="pg-top-in"><a class="pg-brand" href="/">%(brand_html)s</a><a class="pg-home" href="/">Zur Startseite</a></div></header>
<main class="pg">
<p class="pg-crumbs">%(crumbs)s</p>
<h1>%(h1)s</h1>
<p class="lead">%(lead)s</p>
%(calls)s
%(body)s
<nav class="pg-more" aria-label="Weitere Seiten"><h2>Weitere Themen</h2><ul>%(more)s</ul></nav>
</main>
<footer class="pg-foot"><div class="pg-top-in"><span>%(display)s · %(company)s</span><span><a href="/#impressum">Impressum</a> · <a href="/#datenschutz">Datenschutz</a></span></div></footer>
<div class="pg-sticky"><a href="tel:%(stel)s">%(slbl)s</a></div>
</body>
</html>
""" % dict(theme=theme, title=E(title), desc=E(p["desc"]), canon=canon, display=E(display), h1=E(p["h1"]), url=url,
           own=url + p["slug"] + "/", tc_light=tc[0], tc_dark=tc[1],
           css=base_css + CSS, ld=json.dumps(ld, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"),
           brand_html=brand_html, crumbs=crumb_html, lead=E(p["lead"]), calls=call_box(cfg, p.get("calls")), body=p["body"],
           more=more, company=E(cfg["company"]), stel=sticky_tel, slbl=E(sticky_lbl))
