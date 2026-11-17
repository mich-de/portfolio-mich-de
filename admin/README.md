# admin.mdeangelis.me

Editor del diario. Progetto Vercel `mdeangelis-admin` (Root Directory `admin`),
dietro Cloudflare Access (applicazione `admin`, regola "Solo io").

## Variabili su Vercel

| nome            | cosa                                                                 |
|-----------------|----------------------------------------------------------------------|
| `GITHUB_TOKEN`  | chiave fine-grained: solo questo repository, permesso Contents in lettura e scrittura |
| `ADMIN_EMAILS`  | indirizzi ammessi, separati da virgola (gli stessi della regola Cloudflare) |

Facoltative: `CF_TEAM_DOMAIN`, `CF_AUD` (già impostate nel codice),
`GITHUB_REPO`, `GITHUB_BRANCH`.

## Come è protetto

1. Cloudflare Access fa entrare solo le email ammesse (codice usa e getta via email).
2. Ogni chiamata a `/api/editor` verifica comunque il token di Access: firma RS256,
   emittente, AUD, scadenza, email in `ADMIN_EMAILS`. Senza token valido: 401.
3. Le scritture vogliono POST, JSON e origine `https://admin.mdeangelis.me`.
4. Si possono scrivere solo `diario/*.nota` e `diario/media/*`. Il testo passa da
   `nota.py` e i file da `media.py` (foto ripulite) prima del commit su `main`.
5. Pagina con CSP stretta e Trusted Types; nessuna libreria esterna.

## Test

```
python3 -m unittest discover -s admin/test
```
