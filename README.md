# mdeangelis — sito personale

Sito statico di Michele De Angelis, pubblicato su Vercel (`mdeangelis.vercel.app`): una sessione di terminale (neofetch, bat, tree, ls) fatta solo di HTML e CSS.

## Come è fatto

- Solo HTML e CSS in `public/`: nessun JavaScript, nessun codice server, nessuna dipendenza npm.
- Le pagine (`public/index.html`, `public/en/index.html`) sono generate da `strumenti/genera.py`:
  modifica i testi lì e rilancia `python3 strumenti/genera.py`.
- Stile in `public/stile.css`, font JetBrains Mono (OFL) in `public/fonts/`, immagini WebP in `public/img/`.
- Diario in `diario/`: un file `.nota` per post, guida in `diario/COME-SI-SCRIVE.md`.
  L'interprete del formato Nota (`strumenti/nota.py`) è scritto da zero con la sola libreria standard.
- Su Vercel la build lancia i test (`python3 -m unittest discover -s strumenti`) e poi `genera.py`;
  `vercel.json` applica intestazioni di sicurezza rigide
  (CSP `default-src 'none'`, HSTS, COOP/CORP/COEP, Permissions-Policy, niente iframe).

## Perché statico

La versione precedente usava Next.js con una server action. Un sito senza runtime né script
non ha codice eseguibile da attaccare: le vulnerabilità di framework (es. RCE in Next.js) non si applicano.
