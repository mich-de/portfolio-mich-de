# MDEANGELIS Portfolio — AGENTS.md

## Stack
- Sito statico: solo HTML + CSS in `public/`. Nessun JavaScript, nessun codice server, nessuna dipendenza npm.
- Pagine generate da `strumenti/genera.py` (testi IT/EN nel dizionario `TESTI`): `python3 strumenti/genera.py`.
- Monogramma vettoriale in `strumenti/monogramma.txt` (tracciati SVG per rame, grigio, chiaro), inserito inline.
- Stile in `public/stile.css`; font JetBrains Mono variabile (licenza OFL) in `public/fonts/`.
- Diario: post in `diario/*.nota`, linguaggio Nota (`strumenti/nota.py`, solo libreria standard, scritto da zero). Guida: `diario/COME-SI-SCRIVE.md`. Immagini e audio in `diario/media/`: `strumenti/media.py` controlla il formato dai byte e toglie i metadati (EXIF/GPS, XMP, ID3); in `public/diario/media/` (ignorata da git) finiscono solo le copie pulite dei file usati. Pagine in `public/diario/` (indice = git log, post = git show, tipi = rami) più `feed.xml`.
- Test: `python3 -m unittest discover -s strumenti` (interprete, fuzz, pagine generate).
- Deploy: Vercel, `vercel.json` con `framework: null`, `outputDirectory: public`, `buildCommand` che lancia i test e poi `genera.py`. Un errore in un post ferma la build: il sito resta com'era.
- Bozze (`bozza: si`): solo nelle anteprime Vercel (`VERCEL_ENV=preview`) o in locale con `DIARIO_BOZZE=1`.

## Regole
- Non aggiungere script né stili inline: la CSP (`default-src 'none'; style-src 'self'; img-src 'self'; font-src 'self'; media-src 'self'`) li blocca.
- Animazioni solo in CSS e sempre dentro `@media (prefers-reduced-motion: no-preference)`.
- Il codice deve girare anche con Python 3.9: niente `match`, niente f-string con le stesse virgolette annidate o con `\\` dentro le graffe.
- Il sipario iniziale (`.sipario`) usa l'attributo `hidden`: senza CSS resta nascosto.
- Icone delle piattaforme musicali: SVG di Font Awesome Free in `strumenti/icone/` (licenza CC BY 4.0, credito nel piè di pagina e nei commenti degli SVG).
