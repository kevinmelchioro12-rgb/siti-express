#!/usr/bin/env python3
"""
build_sites.py — il motore di clonazione.
Legge prospects.csv + template/site-template.html e genera un sito multilingua
(IT/EN/DE) completo per ogni attivita, in sites/<slug>/index.html.

Uso:  python build_sites.py
CSV:  slug,name,category,city,phone,address,accent,accent2
"""
import csv, json, re, os, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(ROOT, "template", "site-template.html")
CSV_FILE = os.path.join(ROOT, "prospects.csv")
OUT_DIR  = os.path.join(ROOT, "sites")
MAKER = "Kevin Melchioro"
PORTFOLIO_URL = "../../index.html"

# ---------------------------------------------------------------- CHROME (costante per lingua)
CHROME = {
 "it": {
  "navMenu":"Servizi","navStory":"Chi siamo","navReviews":"Recensioni","navVisit":"Dove siamo",
  "btnCall":"Chiama","btnReserve":"Chiama ora","btnSee":"Scopri di più","openNow":"Aperto ora",
  "hoursTitle":"Orari","hoursWeekLbl":"Lun – Ven","hoursSatLbl":"Sabato","hoursSunLbl":"Domenica","closed":"Chiuso",
  "knownEyebrow":"Perché sceglierci","storyEyebrow":"Chi siamo",
  "stat1Lbl":"Soddisfazione clienti","stat2Lbl":"Valutazione media","stat3Lbl":"Clienti serviti","stat4Lbl":"Sempre al tuo fianco",
  "galleryEyebrow":"Uno sguardo","galleryTitle":"Dentro {name}.",
  "reviewsEyebrow":"Dicono di noi","reviewsTitle":"Le parole dei clienti.",
  "q1":"Servizio impeccabile e persone che ti mettono a tuo agio. Torno sempre volentieri.","q1who":"Maya R. · Cliente abituale",
  "q2":"Professionali, puntuali e onesti sul prezzo. Esattamente quello che cercavo.","q2who":"Daniel K. · Recensione Google",
  "q3":"Mi hanno trattato come uno di famiglia fin dal primo momento. Consigliatissimo.","q3who":"Priya S. · Prima visita",
  "visitEyebrow":"Vieni a trovarci","visitTitle":"Passa da {name}.","credit":"Sito realizzato da",
 },
 "en": {
  "navMenu":"Services","navStory":"About","navReviews":"Reviews","navVisit":"Visit",
  "btnCall":"Call","btnReserve":"Call now","btnSee":"See more","openNow":"Open now",
  "hoursTitle":"Hours","hoursWeekLbl":"Mon – Fri","hoursSatLbl":"Saturday","hoursSunLbl":"Sunday","closed":"Closed",
  "knownEyebrow":"Why choose us","storyEyebrow":"About us",
  "stat1Lbl":"Customer satisfaction","stat2Lbl":"Average rating","stat3Lbl":"Customers served","stat4Lbl":"Always here for you",
  "galleryEyebrow":"A look","galleryTitle":"Inside {name}.",
  "reviewsEyebrow":"Kind words","reviewsTitle":"What our customers say.",
  "q1":"Flawless service and people who put you at ease. I always come back happily.","q1who":"Maya R. · Regular",
  "q2":"Professional, on time, and honest about price. Exactly what I was looking for.","q2who":"Daniel K. · Google review",
  "q3":"They treated me like family from the very first moment. Highly recommended.","q3who":"Priya S. · First visit",
  "visitEyebrow":"Come see us","visitTitle":"Visit {name}.","credit":"Website by",
 },
 "de": {
  "navMenu":"Leistungen","navStory":"Über uns","navReviews":"Bewertungen","navVisit":"Anfahrt",
  "btnCall":"Anrufen","btnReserve":"Jetzt anrufen","btnSee":"Mehr erfahren","openNow":"Jetzt geöffnet",
  "hoursTitle":"Öffnungszeiten","hoursWeekLbl":"Mo – Fr","hoursSatLbl":"Samstag","hoursSunLbl":"Sonntag","closed":"Geschlossen",
  "knownEyebrow":"Warum wir","storyEyebrow":"Über uns",
  "stat1Lbl":"Kundenzufriedenheit","stat2Lbl":"Durchschnittsbewertung","stat3Lbl":"Betreute Kunden","stat4Lbl":"Immer für Sie da",
  "galleryEyebrow":"Ein Blick","galleryTitle":"Bei {name}.",
  "reviewsEyebrow":"Stimmen","reviewsTitle":"Was unsere Kunden sagen.",
  "q1":"Tadelloser Service und Menschen, bei denen man sich wohlfühlt. Ich komme immer gerne wieder.","q1who":"Maya R. · Stammkundin",
  "q2":"Professionell, pünktlich und ehrlich beim Preis. Genau das, was ich gesucht habe.","q2who":"Daniel K. · Google-Bewertung",
  "q3":"Man hat mich vom ersten Moment an wie Familie behandelt. Sehr zu empfehlen.","q3who":"Priya S. · Erster Besuch",
  "visitEyebrow":"Besuchen Sie uns","visitTitle":"Kommen Sie zu {name}.","credit":"Website von",
 },
}

# ---------------------------------------------------------------- CATEGORY packs (creativi, per categoria)
CAT = {
 "restaurant": {
  "it":{"heroEyebrow":"Cucina di quartiere","heroTitle":"Un tavolo che sa di <em>casa</em>.","heroTagline":"Piatti di stagione, materie prime del territorio e l'accoglienza che rende speciale anche un martedì.","knownTitle":"Quello per cui ci scelgono.","card1Title":"Cucina di stagione","card1Text":"Un menù che cambia con il mercato, con prodotti freschi e fornitori locali.","card2Title":"Una carta dei vini curata","card2Text":"Etichette scelte con cura, molte disponibili al calice.","card3Title":"Un ambiente che accoglie","card3Text":"Luce calda, musica giusta e un bancone dove stare bene anche da soli.","storyTitle":"Nati dalla passione per la buona tavola.","storyP1":"{name} è cresciuto a {city} un piatto alla volta, diventando il posto dove i clienti tornano come a casa.","storyP2":"La nostra ricetta è semplice: ingredienti onesti, fuoco buono e un team felice di vederti entrare.","g1":"La sala","g2":"I nostri piatti","g3":"Il bancone","g4":"I vini","g5":"Le serate da {name}","g6":"I dolci"},
  "en":{"heroEyebrow":"Neighborhood kitchen","heroTitle":"A table that feels like <em>home</em>.","heroTagline":"Seasonal plates, local ingredients, and the kind of welcome that makes even a Tuesday feel special.","knownTitle":"What we're known for.","card1Title":"Seasonal cooking","card1Text":"A menu that changes with the market — fresh produce and local suppliers.","card2Title":"A curated wine list","card2Text":"Carefully chosen labels, many available by the glass.","card3Title":"A room that welcomes","card3Text":"Warm light, the right music, and a bar that's great even solo.","storyTitle":"Born from a love of good food.","storyP1":"{name} grew up in {city} one plate at a time, becoming the place regulars treat like home.","storyP2":"Our recipe is simple: honest ingredients, good fire, and a team happy to see you walk in.","g1":"The room","g2":"Our plates","g3":"The bar","g4":"The wines","g5":"Evenings at {name}","g6":"Desserts"},
  "de":{"heroEyebrow":"Küche im Viertel","heroTitle":"Ein Tisch, der sich wie <em>Zuhause</em> anfühlt.","heroTagline":"Saisonale Gerichte, regionale Zutaten und eine Herzlichkeit, die sogar einen Dienstag besonders macht.","knownTitle":"Wofür man uns kennt.","card1Title":"Saisonale Küche","card1Text":"Eine Karte, die mit dem Markt wechselt — frische Produkte, regionale Lieferanten.","card2Title":"Eine ausgewählte Weinkarte","card2Text":"Sorgfältig gewählte Etiketten, viele auch glasweise.","card3Title":"Ein Raum, der willkommen heißt","card3Text":"Warmes Licht, die richtige Musik und eine Bar, an der man auch allein gern sitzt.","storyTitle":"Aus Liebe zum guten Essen entstanden.","storyP1":"{name} ist in {city} Teller für Teller gewachsen — zu dem Ort, an den Stammgäste wie nach Hause zurückkehren.","storyP2":"Unser Rezept ist einfach: ehrliche Zutaten, gutes Feuer und ein Team, das sich freut, wenn Sie hereinkommen.","g1":"Der Raum","g2":"Unsere Gerichte","g3":"Die Bar","g4":"Die Weine","g5":"Abende bei {name}","g6":"Desserts"},
 },
 "cafe": {
  "it":{"heroEyebrow":"Caffè & pasticceria","heroTitle":"Il tuo angolo di <em>buongiorno</em>.","heroTagline":"Caffè di qualità, dolci fatti in casa e un posto dove rallentare, a {city}.","knownTitle":"Perché la gente torna.","card1Title":"Caffè come si deve","card1Text":"Miscele selezionate ed espresso fatto a regola d'arte.","card2Title":"Dolci fatti in casa","card2Text":"Cornetti, torte e lievitati sfornati ogni mattina.","card3Title":"Un'atmosfera che coccola","card3Text":"Wi-Fi, divani e il sottofondo giusto per lavorare o leggere.","storyTitle":"Un piccolo posto, fatto con cura.","storyP1":"{name} è nato a {city} per dare al quartiere un buon motivo per fermarsi.","storyP2":"Ingredienti veri, persone gentili e quel profumo di caffè che ti fa venire voglia di restare.","g1":"Il bancone","g2":"I dolci","g3":"Il caffè","g4":"L'angolo lettura","g5":"Le mattine da {name}","g6":"Da asporto"},
  "en":{"heroEyebrow":"Coffee & pastry","heroTitle":"Your corner of <em>good morning</em>.","heroTagline":"Quality coffee, homemade pastries, and a place to slow down, in {city}.","knownTitle":"Why people come back.","card1Title":"Coffee done right","card1Text":"Selected blends and espresso pulled with care.","card2Title":"Homemade pastries","card2Text":"Croissants, cakes and bakes out of the oven every morning.","card3Title":"A cosy atmosphere","card3Text":"Wi-Fi, sofas and the right background to work or read.","storyTitle":"A small place, made with care.","storyP1":"{name} was born in {city} to give the neighborhood a good reason to pause.","storyP2":"Real ingredients, kind people, and that smell of coffee that makes you want to stay.","g1":"The counter","g2":"The pastries","g3":"The coffee","g4":"Reading nook","g5":"Mornings at {name}","g6":"Takeaway"},
  "de":{"heroEyebrow":"Kaffee & Konditorei","heroTitle":"Dein Eck zum <em>Guten Morgen</em>.","heroTagline":"Guter Kaffee, hausgemachte Mehlspeisen und ein Ort zum Entschleunigen, in {city}.","knownTitle":"Warum man wiederkommt.","card1Title":"Kaffee, wie er sein soll","card1Text":"Ausgewählte Mischungen und sorgfältig gebrühter Espresso.","card2Title":"Hausgemachte Mehlspeisen","card2Text":"Croissants, Kuchen und Gebäck — jeden Morgen frisch.","card3Title":"Eine gemütliche Atmosphäre","card3Text":"WLAN, Sofas und der richtige Sound zum Arbeiten oder Lesen.","storyTitle":"Ein kleiner Ort, mit Liebe gemacht.","storyP1":"{name} entstand in {city}, um dem Viertel einen guten Grund zum Innehalten zu geben.","storyP2":"Echte Zutaten, freundliche Menschen und dieser Kaffeeduft, der zum Bleiben einlädt.","g1":"Die Theke","g2":"Die Mehlspeisen","g3":"Der Kaffee","g4":"Leseecke","g5":"Morgende bei {name}","g6":"Zum Mitnehmen"},
 },
 "beauty": {
  "it":{"heroEyebrow":"Studio di bellezza","heroTitle":"La tua bellezza, <em>in buone mani</em>.","heroTagline":"Trattamenti su misura e cura dei dettagli, in un ambiente rilassante a {city}.","knownTitle":"Perché ti affidi a noi.","card1Title":"Trattamenti su misura","card1Text":"Ogni servizio pensato sulla tua pelle e sui tuoi desideri.","card2Title":"Prodotti di qualità","card2Text":"Linee professionali e tecniche sempre aggiornate.","card3Title":"Un'oasi di relax","card3Text":"Un'ora tutta per te, lontano dalla fretta della giornata.","storyTitle":"Passione per la cura della persona.","storyP1":"{name} è il punto di riferimento a {city} per chi vuole sentirsi al meglio.","storyP2":"Ascolto, mani esperte e attenzione ai dettagli: esci sempre con il sorriso.","g1":"Lo studio","g2":"I trattamenti","g3":"I dettagli","g4":"I prodotti","g5":"Il relax da {name}","g6":"Prima / dopo"},
  "en":{"heroEyebrow":"Beauty studio","heroTitle":"Your beauty, <em>in good hands</em>.","heroTagline":"Tailored treatments and attention to detail, in a relaxing space in {city}.","knownTitle":"Why you'll trust us.","card1Title":"Tailored treatments","card1Text":"Every service designed around your skin and your wishes.","card2Title":"Quality products","card2Text":"Professional lines and always up-to-date techniques.","card3Title":"A relaxing oasis","card3Text":"An hour just for you, away from the rush of the day.","storyTitle":"A passion for personal care.","storyP1":"{name} is the go-to in {city} for anyone who wants to feel their best.","storyP2":"Listening, skilled hands and attention to detail: you always leave smiling.","g1":"The studio","g2":"Treatments","g3":"The details","g4":"Products","g5":"Relaxing at {name}","g6":"Before / after"},
  "de":{"heroEyebrow":"Beauty-Studio","heroTitle":"Ihre Schönheit, <em>in guten Händen</em>.","heroTagline":"Maßgeschneiderte Behandlungen und Liebe zum Detail, in entspannter Atmosphäre in {city}.","knownTitle":"Warum Sie uns vertrauen.","card1Title":"Individuelle Behandlungen","card1Text":"Jede Leistung auf Ihre Haut und Ihre Wünsche abgestimmt.","card2Title":"Hochwertige Produkte","card2Text":"Professionelle Linien und stets aktuelle Techniken.","card3Title":"Eine Oase der Ruhe","card3Text":"Eine Stunde nur für Sie, weg von der Hektik des Tages.","storyTitle":"Leidenschaft für Pflege.","storyP1":"{name} ist in {city} die erste Adresse für alle, die sich rundum wohlfühlen möchten.","storyP2":"Zuhören, erfahrene Hände und Liebe zum Detail: Sie gehen immer mit einem Lächeln.","g1":"Das Studio","g2":"Behandlungen","g3":"Die Details","g4":"Produkte","g5":"Entspannen bei {name}","g6":"Vorher / nachher"},
 },
 "auto": {
  "it":{"heroEyebrow":"Officina di fiducia","heroTitle":"La tua auto, <em>in mani sicure</em>.","heroTagline":"Riparazioni oneste, tempi rispettati e prezzi chiari, a {city}.","knownTitle":"Perché ti fidi di noi.","card1Title":"Diagnosi e riparazioni","card1Text":"Meccanici esperti e strumenti aggiornati per ogni intervento.","card2Title":"Preventivi chiari","card2Text":"Sai cosa paghi prima di iniziare. Nessuna sorpresa.","card3Title":"Tempi rispettati","card3Text":"Ti riconsegniamo l'auto quando promesso, pronta a ripartire.","storyTitle":"Onestà e competenza, da anni.","storyP1":"{name} è l'officina a {city} dove le persone tornano perché si fidano.","storyP2":"Trattiamo ogni auto come fosse la nostra: lavoro fatto bene, parola mantenuta.","g1":"L'officina","g2":"Il team","g3":"La diagnosi","g4":"I ricambi","g5":"Al lavoro da {name}","g6":"Pronta a partire"},
  "en":{"heroEyebrow":"Trusted garage","heroTitle":"Your car, <em>in safe hands</em>.","heroTagline":"Honest repairs, deadlines kept and clear prices, in {city}.","knownTitle":"Why you'll trust us.","card1Title":"Diagnostics & repairs","card1Text":"Skilled mechanics and up-to-date tools for every job.","card2Title":"Clear quotes","card2Text":"You know what you pay before we start. No surprises.","card3Title":"Deadlines kept","card3Text":"We hand your car back when promised, ready to go.","storyTitle":"Honesty and skill, for years.","storyP1":"{name} is the garage in {city} where people come back because they trust it.","storyP2":"We treat every car like our own: work done right, word kept.","g1":"The garage","g2":"The team","g3":"Diagnostics","g4":"Parts","g5":"At work at {name}","g6":"Ready to go"},
  "de":{"heroEyebrow":"Werkstatt des Vertrauens","heroTitle":"Ihr Auto, <em>in sicheren Händen</em>.","heroTagline":"Ehrliche Reparaturen, eingehaltene Termine und klare Preise, in {city}.","knownTitle":"Warum Sie uns vertrauen.","card1Title":"Diagnose & Reparatur","card1Text":"Erfahrene Mechaniker und moderne Geräte für jeden Auftrag.","card2Title":"Klare Kostenvoranschläge","card2Text":"Sie wissen, was Sie zahlen, bevor wir beginnen. Keine Überraschungen.","card3Title":"Termine eingehalten","card3Text":"Wir geben Ihr Auto zurück, wenn versprochen — startklar.","storyTitle":"Ehrlichkeit und Können, seit Jahren.","storyP1":"{name} ist die Werkstatt in {city}, zu der man zurückkommt, weil man ihr vertraut.","storyP2":"Wir behandeln jedes Auto wie unser eigenes: gute Arbeit, gehaltenes Wort.","g1":"Die Werkstatt","g2":"Das Team","g3":"Diagnose","g4":"Ersatzteile","g5":"Bei der Arbeit bei {name}","g6":"Startklar"},
 },
 "gym": {
  "it":{"heroEyebrow":"Palestra & fitness","heroTitle":"Allena la <em>tua</em> forza.","heroTagline":"Attrezzi top, corsi per ogni livello e trainer che ti seguono davvero, a {city}.","knownTitle":"Perché allenarti da noi.","card1Title":"Attrezzatura completa","card1Text":"Macchine moderne e area pesi liberi sempre in ordine.","card2Title":"Corsi per tutti","card2Text":"Dal functional allo yoga: trovi l'orario che fa per te.","card3Title":"Trainer qualificati","card3Text":"Schede su misura e supporto costante, non sei mai solo.","storyTitle":"Più di una palestra.","storyP1":"{name} è il punto di ritrovo a {city} per chi vuole stare bene, dentro e fuori.","storyP2":"Ambiente motivante, pulito e accogliente: qui i risultati arrivano e la voglia di tornare anche.","g1":"La sala pesi","g2":"Il cardio","g3":"I corsi","g4":"Functional","g5":"Allenarsi da {name}","g6":"Gli spogliatoi"},
  "en":{"heroEyebrow":"Gym & fitness","heroTitle":"Train <em>your</em> strength.","heroTagline":"Top equipment, classes for every level and trainers who really follow you, in {city}.","knownTitle":"Why train with us.","card1Title":"Full equipment","card1Text":"Modern machines and a free-weights area always in order.","card2Title":"Classes for all","card2Text":"From functional to yoga: find the schedule that fits you.","card3Title":"Qualified trainers","card3Text":"Tailored plans and constant support — you're never alone.","storyTitle":"More than a gym.","storyP1":"{name} is the meeting point in {city} for anyone who wants to feel good, inside and out.","storyP2":"A motivating, clean and welcoming space: results come, and so does the urge to return.","g1":"The weights room","g2":"Cardio","g3":"Classes","g4":"Functional","g5":"Training at {name}","g6":"The changing rooms"},
  "de":{"heroEyebrow":"Fitnessstudio","heroTitle":"Trainiere <em>deine</em> Kraft.","heroTagline":"Top-Geräte, Kurse für jedes Level und Trainer, die dich wirklich begleiten, in {city}.","knownTitle":"Warum bei uns trainieren.","card1Title":"Komplette Ausstattung","card1Text":"Moderne Geräte und ein stets gepflegter Freihantelbereich.","card2Title":"Kurse für alle","card2Text":"Von Functional bis Yoga: Finde den passenden Zeitplan.","card3Title":"Qualifizierte Trainer","card3Text":"Individuelle Pläne und ständige Betreuung — du bist nie allein.","storyTitle":"Mehr als ein Studio.","storyP1":"{name} ist in {city} der Treffpunkt für alle, die sich rundum wohlfühlen wollen.","storyP2":"Eine motivierende, saubere und einladende Umgebung: Ergebnisse kommen — und die Lust wiederzukommen auch.","g1":"Der Kraftbereich","g2":"Cardio","g3":"Kurse","g4":"Functional","g5":"Training bei {name}","g6":"Die Umkleiden"},
 },
 "hotel": {
  "it":{"heroEyebrow":"Hotel & ospitalità","heroTitle":"Il tuo soggiorno, <em>su misura</em>.","heroTagline":"Camere accoglienti, colazione genuina e una posizione perfetta per scoprire {city}.","knownTitle":"Perché sceglierci.","card1Title":"Camere confortevoli","card1Text":"Spazi curati, letti comodi e tutto ciò che serve per riposare.","card2Title":"Colazione del territorio","card2Text":"Prodotti locali e genuini per iniziare bene la giornata.","card3Title":"Posizione strategica","card3Text":"A pochi passi da tutto, perfetto per turismo e lavoro.","storyTitle":"Ospitalità che si sente.","storyP1":"{name} accoglie a {city} viaggiatori da tutta Europa, come fossero a casa.","storyP2":"Personale attento, ambienti curati e quei dettagli che trasformano una notte in un bel ricordo.","g1":"Le camere","g2":"La colazione","g3":"La hall","g4":"I dintorni","g5":"Il soggiorno da {name}","g6":"I dettagli"},
  "en":{"heroEyebrow":"Hotel & hospitality","heroTitle":"Your stay, <em>tailored</em>.","heroTagline":"Cosy rooms, a genuine breakfast and a perfect base to discover {city}.","knownTitle":"Why choose us.","card1Title":"Comfortable rooms","card1Text":"Well-kept spaces, comfy beds and everything you need to rest.","card2Title":"Local breakfast","card2Text":"Genuine local products to start the day right.","card3Title":"Great location","card3Text":"A few steps from everything — perfect for tourism and business.","storyTitle":"Hospitality you can feel.","storyP1":"{name} welcomes travellers from across Europe to {city}, as if they were home.","storyP2":"Attentive staff, refined spaces and the details that turn a night into a fond memory.","g1":"The rooms","g2":"Breakfast","g3":"The lobby","g4":"The surroundings","g5":"Your stay at {name}","g6":"The details"},
  "de":{"heroEyebrow":"Hotel & Gastlichkeit","heroTitle":"Ihr Aufenthalt, <em>maßgeschneidert</em>.","heroTagline":"Gemütliche Zimmer, ein echtes Frühstück und eine perfekte Lage, um {city} zu entdecken.","knownTitle":"Warum wir.","card1Title":"Komfortable Zimmer","card1Text":"Gepflegte Räume, bequeme Betten und alles, was Sie zum Ausruhen brauchen.","card2Title":"Regionales Frühstück","card2Text":"Echte regionale Produkte für einen guten Start in den Tag.","card3Title":"Top-Lage","card3Text":"Wenige Schritte von allem — ideal für Urlaub und Geschäft.","storyTitle":"Gastlichkeit, die man spürt.","storyP1":"{name} empfängt in {city} Reisende aus ganz Europa — als wären sie zu Hause.","storyP2":"Aufmerksames Personal, gepflegte Räume und die Details, die aus einer Nacht eine schöne Erinnerung machen.","g1":"Die Zimmer","g2":"Frühstück","g3":"Die Lobby","g4":"Die Umgebung","g5":"Ihr Aufenthalt bei {name}","g6":"Die Details"},
 },
 "barber": {
  "it":{"heroEyebrow":"Barbiere","heroTitle":"Stile, <em>rasoio</em> e carattere.","heroTagline":"Taglio, barba e cura dell'uomo, con la precisione di una volta, a {city}.","knownTitle":"Perché venire da noi.","card1Title":"Taglio su misura","card1Text":"Classico o moderno: il look giusto per te, fatto a regola d'arte.","card2Title":"Barba e rasoio","card2Text":"Rasatura tradizionale, panno caldo e prodotti di qualità.","card3Title":"Atmosfera vera","card3Text":"Una poltrona, due chiacchiere e l'esperienza del barbiere di fiducia.","storyTitle":"Il mestiere del barbiere.","storyP1":"{name} è il barbiere a {city} dove gli uomini tornano per sentirsi a posto.","storyP2":"Mani esperte, attenzione al dettaglio e quel rito che ti fa uscire più sicuro di prima.","g1":"La bottega","g2":"I tagli","g3":"La barba","g4":"I prodotti","g5":"Da {name}","g6":"Il dettaglio"},
  "en":{"heroEyebrow":"Barbershop","heroTitle":"Style, <em>razor</em> and character.","heroTagline":"Cuts, beards and men's grooming with old-school precision, in {city}.","knownTitle":"Why come to us.","card1Title":"Tailored cuts","card1Text":"Classic or modern: the right look for you, done properly.","card2Title":"Beard & razor","card2Text":"Traditional shave, hot towel and quality products.","card3Title":"A real atmosphere","card3Text":"A chair, a chat and the experience of your trusted barber.","storyTitle":"The barber's craft.","storyP1":"{name} is the barbershop in {city} where men come back to feel sharp.","storyP2":"Skilled hands, attention to detail and that ritual that sends you out more confident than before.","g1":"The shop","g2":"The cuts","g3":"The beard","g4":"Products","g5":"At {name}","g6":"The detail"},
  "de":{"heroEyebrow":"Barbershop","heroTitle":"Stil, <em>Rasiermesser</em> und Charakter.","heroTagline":"Schnitt, Bart und Männerpflege mit Präzision wie früher, in {city}.","knownTitle":"Warum zu uns.","card1Title":"Individuelle Schnitte","card1Text":"Klassisch oder modern: der richtige Look für dich, sauber gemacht.","card2Title":"Bart & Rasiermesser","card2Text":"Traditionelle Rasur, heißes Tuch und hochwertige Produkte.","card3Title":"Echte Atmosphäre","card3Text":"Ein Stuhl, ein Gespräch und die Erfahrung deines Barbiers des Vertrauens.","storyTitle":"Das Handwerk des Barbiers.","storyP1":"{name} ist der Barbershop in {city}, zu dem Männer zurückkommen, um sich top zu fühlen.","storyP2":"Erfahrene Hände, Liebe zum Detail und dieses Ritual, das dich selbstbewusster hinausgehen lässt.","g1":"Der Laden","g2":"Die Schnitte","g3":"Der Bart","g4":"Produkte","g5":"Bei {name}","g6":"Das Detail"},
 },
 "generic": {
  "it":{"heroEyebrow":"Attività di quartiere","heroTitle":"Il servizio che {city} <em>sceglie</em>.","heroTagline":"Lavoro fatto bene, persone di cui ti puoi fidare, qui a {city}.","knownTitle":"Perché sceglierci.","card1Title":"Servizio di qualità","card1Text":"Cura, competenza e attenzione in ogni cosa che facciamo.","card2Title":"Persone affidabili","card2Text":"Puntuali, corretti e sempre disponibili. Diciamo le cose come stanno.","card3Title":"Clienti soddisfatti","card3Text":"La maggior parte di chi ci sceglie torna e ci consiglia.","storyTitle":"Vicini, da sempre.","storyP1":"{name} lavora a {city} con un'idea semplice: trattare ogni cliente come si deve.","storyP2":"Niente promesse vuote: solo lavoro fatto bene e parola mantenuta.","g1":"Da noi","g2":"Il lavoro","g3":"Il team","g4":"I dettagli","g5":"Con {name}","g6":"I risultati"},
  "en":{"heroEyebrow":"Local business","heroTitle":"The service {city} <em>chooses</em>.","heroTagline":"Work done right, people you can trust, here in {city}.","knownTitle":"Why choose us.","card1Title":"Quality service","card1Text":"Care, skill and attention in everything we do.","card2Title":"Reliable people","card2Text":"On time, fair and always available. We tell it straight.","card3Title":"Happy customers","card3Text":"Most who choose us come back and recommend us.","storyTitle":"Close to you, always.","storyP1":"{name} works in {city} with one simple idea: treat every customer right.","storyP2":"No empty promises: just good work and a word kept.","g1":"With us","g2":"The work","g3":"The team","g4":"The details","g5":"With {name}","g6":"Results"},
  "de":{"heroEyebrow":"Betrieb vor Ort","heroTitle":"Der Service, den {city} <em>wählt</em>.","heroTagline":"Gute Arbeit, Menschen, denen Sie vertrauen können — hier in {city}.","knownTitle":"Warum wir.","card1Title":"Qualitätsservice","card1Text":"Sorgfalt, Können und Aufmerksamkeit in allem, was wir tun.","card2Title":"Verlässliche Menschen","card2Text":"Pünktlich, fair und immer erreichbar. Wir sagen es ehrlich.","card3Title":"Zufriedene Kunden","card3Text":"Die meisten kommen wieder und empfehlen uns weiter.","storyTitle":"Immer in Ihrer Nähe.","storyP1":"{name} arbeitet in {city} mit einer einfachen Idee: jeden Kunden richtig behandeln.","storyP2":"Keine leeren Versprechen: nur gute Arbeit und ein gehaltenes Wort.","g1":"Bei uns","g2":"Die Arbeit","g3":"Das Team","g4":"Die Details","g5":"Mit {name}","g6":"Ergebnisse"},
 },
}

LABELS = {  # per <title> e meta (in italiano, lingua di default)
 "restaurant":"Ristorante","cafe":"Caffè & Pasticceria","barber":"Barbiere","beauty":"Studio di Bellezza",
 "gym":"Palestra","hotel":"Hotel","auto":"Officina","generic":"Attività locale",
}
SYN = {  # NB: 'barber' prima di 'cafe' perché "barbiere" contiene "bar"
 "restaurant":["restaurant","ristorante","trattoria","pizzeria","osteria","gasthaus","gasthof","lokal"],
 "barber":["barbiere","barbershop","barbier","barber"],
 "cafe":["cafe","café","caffe","caffè","bar","coffee","kaffee","konditorei","pasticceria","bakery","panetteria","bäckerei","baeckerei"],
 "beauty":["beauty","bellezza","estetica","centro estetico","parrucchiere","hair","salon","friseur","kosmetik","nails","spa"],
 "gym":["palestra","gym","fitness","fitnessstudio","crossfit","wellness"],
 "hotel":["hotel","albergo","bed and breakfast","b&b","pensione","herberge","resort","gasthof"],
 "auto":["autofficina","auto","car","garage","officina","werkstatt","mechanic","meccanico","kfz"],
}

def cat_key(raw):
    r = (raw or "").strip().lower()
    for key, words in SYN.items():
        if any(w in r for w in words):
            return key
    return "generic"

def fill(s, name, city):
    return s.replace("{name}", name).replace("{city}", city)

def phone_href(p):
    p = (p or "").strip()
    keep = "+" + re.sub(r"\D", "", p) if p.startswith("+") else re.sub(r"\D", "", p)
    return keep

def build_i18n(name, city, ck):
    out = {}
    for lang in ("it", "en", "de"):
        d = {}
        for k, v in CHROME[lang].items():
            d[k] = fill(v, name, city)
        for k, v in CAT[ck][lang].items():
            d[k] = fill(v, name, city)
        out[lang] = d
    return out

def main():
    with open(TEMPLATE, encoding="utf-8") as f:
        tpl = f.read()
    os.makedirs(OUT_DIR, exist_ok=True)
    built = []
    with open(CSV_FILE, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if not row.get("slug"): continue
            name = row["name"].strip(); city = row.get("city","").strip()
            ck = cat_key(row.get("category",""))
            i18n = build_i18n(name, city, ck)
            html = tpl
            # 1) inietta il dizionario lingue
            html = html.replace("/*__I18N__*/{}", json.dumps(i18n, ensure_ascii=False))
            # 2) riempi i default visibili con l'italiano
            for k, v in i18n["it"].items():
                html = html.replace(f"__{k}__", v)
            # 3) token statici
            tokens = {
                "DEFAULT_LANG":"it",
                "NAME": name,
                "TITLE_SUFFIX": f"{LABELS[ck]} a {city}",
                "META_DESC": f"{name}, {LABELS[ck].lower()} a {city}. Telefono {row.get('phone','').strip()}. Servizi, orari e contatti.",
                "INK": (row.get("ink") or "#1c1714").strip(),
                "PAPER": (row.get("paper") or "#f5efe6").strip(),
                "ACCENT": (row.get("accent") or "#c8602f").strip(),
                "ACCENT2": (row.get("accent2") or "#e8a23d").strip(),
                "PHONE": row.get("phone","").strip(),
                "PHONE_HREF": phone_href(row.get("phone","")),
                "ADDRESS": row.get("address","").strip(),
                "MAPS_URL": "https://maps.google.com/?q=" + urllib.parse.quote(f"{row.get('address','')} {city}".strip()),
                "STAT1": row.get("stat1") or "100%",
                "STAT2": row.get("stat2") or "★ 4,9",
                "STAT3": row.get("stat3") or "1.200+",
                "STAT4": row.get("stat4") or "7/7",
                "HOURS_WEEK": row.get("hours_week") or "09:00 – 18:00",
                "HOURS_SAT": row.get("hours_sat") or "09:00 – 13:00",
                "PORTFOLIO_URL": PORTFOLIO_URL,
                "MAKER": MAKER,
            }
            for k, v in tokens.items():
                html = html.replace("{{"+k+"}}", str(v))
            site_dir = os.path.join(OUT_DIR, row["slug"])
            os.makedirs(site_dir, exist_ok=True)
            with open(os.path.join(site_dir, "index.html"), "w", encoding="utf-8") as out:
                out.write(html)
            left = re.findall(r"__[a-zA-Z0-9]+__|{{[A-Z0-9_]+}}", html)
            built.append((row["slug"], name, ck, len(left)))
    print(f"Generati {len(built)} siti in sites/:")
    for slug, name, ck, left in built:
        flag = "  ⚠ placeholder residui!" if left else ""
        print(f"  • {slug:22s} {name:26s} [{ck}]{flag}")

if __name__ == "__main__":
    main()
