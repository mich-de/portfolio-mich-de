# MDEANGELIS Portfolio — AGENTS.md

## Stack
- Sito statico: solo HTML + CSS in `public/`. Nessun JavaScript, nessun codice server, nessuna dipendenza npm.
- Pagine generate da `strumenti/genera.py` (testi IT/EN nel dizionario `TESTI`): `python3 strumenti/genera.py`.
- Monogramma vettoriale in `strumenti/monogramma.txt` (tracciati SVG per rame, grigio, chiaro), inserito inline.
- Stile in `public/stile.css`; font JetBrains Mono variabile (licenza OFL) in `public/fonts/`.
- Deploy: Vercel, `vercel.json` con `framework: null`, `outputDirectory: public`.

## Regole
- Non aggiungere script né stili inline: la CSP (`default-src 'none'; style-src 'self'; img-src 'self'; font-src 'self'`) li blocca.
- Animazioni solo in CSS e sempre dentro `@media (prefers-reduced-motion: no-preference)`.
- Il sipario iniziale (`.sipario`) usa l'attributo `hidden`: senza CSS resta nascosto.
- Icone delle piattaforme musicali: SVG di Font Awesome Free in `strumenti/icone/` (licenza CC BY 4.0, credito nel piè di pagina e nei commenti degli SVG).
