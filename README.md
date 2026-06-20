# Siti Express 🌍 — siti web multilingua (IT/EN/DE) per attività locali

Sistema completo per **creare e vendere** siti one-page multilingua, in giornata, con un laptop.
Pensato per la zona di confine (Italia / Austria / turismo), dove IT + EN + DE fa la differenza.

**Demo live:** https://kevinmelchioro12-rgb.github.io/siti-express/

---

## ⚠️ Importante — niente siti di terzi pubblicati senza consenso
Questo repo contiene la **tua cassetta degli attrezzi** + 4 attività **fittizie** di esempio (portfolio).
NON pubblichiamo online siti con nome/telefono/indirizzo *reali* di attività che non te l'hanno chiesto:
è impersonazione, confonde i loro clienti e ti brucia la reputazione.
La vendita giusta è **privata**: generi un esempio *per quel titolare* e glielo mostri solo a lui.

---

## 📁 Cosa c'è dentro

| File / cartella | Cos'è |
|---|---|
| `index.html` | Homepage **portfolio** multilingua con le 4 demo e i prezzi (= pagina GitHub Pages) |
| `template/site-template.html` | Il template multilingua con i segnaposto |
| `build_sites.py` | **Il motore**: legge `prospects.csv` + template → genera un sito per ogni attività |
| `prospects.csv` | La lista delle attività (una riga = un sito) |
| `sites/<slug>/index.html` | I siti generati (uno a cartella) |
| `PRICING.md` | Prezzi in IT/EN/DE |

---

## 🚀 Come generare i siti

1. Apri `prospects.csv` e compila una riga per attività:
   ```
   slug,name,category,city,phone,address,accent,accent2
   mario-bar,Bar da Mario,bar,Tarvisio,+39 0428 123456,Via Roma 5 · Tarvisio,#c8602f,#e8a23d
   ```
   - **slug** = nome cartella (minuscolo, con trattini)
   - **category** = `ristorante` / `bar` / `bellezza` / `officina` (o lascia generico) → sceglie i testi
   - **accent / accent2** = i due colori del brand (formato `#rrggbb`)
2. Lancia il motore:
   ```
   python build_sites.py
   ```
3. Trovi i siti pronti in `sites/<slug>/index.html`. Ognuno ha già IT, EN e DE con selettore lingua.

> I testi sono già scritti in 3 lingue per categoria. Devi solo dare nome, città, telefono, indirizzo e colori.

---

## 🌐 Pubblicare (GitHub Pages, gratis)

Questo repo è già pubblicato su Pages. Dopo ogni modifica:
```
git add .
git commit -m "aggiorno i siti"
git push
```
In ~1 minuto è online su https://kevinmelchioro12-rgb.github.io/siti-express/

**Per un cliente vero** che ti ha detto sì, l'alternativa più semplice e privata:
trascina la cartella `sites/<suo-nome>` su **https://app.netlify.com/drop** → link live solo per lui.

---

## 💶 Prezzi
Vedi [`PRICING.md`](PRICING.md). In breve: **Starter €150 · Standard €390 (consigliato) · Completo €890.**

---

## 🔁 Il giro completo (riassunto)
**Trova attività con sito assente/vecchio → genera l'esempio → mostralo al titolare → incassa → ripeti.**
Vinci con il multilingua: nella zona di confine nessuno lo offre di serie.
