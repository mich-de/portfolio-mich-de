"""Nota: il linguaggio del diario di mdeangelis.me (versione 1).

Scritto da zero, solo libreria standard di Python. Gira soltanto quando si
generano le pagine: sul sito arriva HTML statico, mai codice eseguibile.

Regole di sicurezza
- Niente HTML scritto a mano: tutto il testo viene sempre "escapato".
- L'interprete produce solo tag di una lista chiusa (vedi TAG_AMMESSI).
- I link accettano solo indirizzi https:// con caratteri sicuri.
- Qualsiasi errore ferma la generazione con file e numero di riga:
  un post sbagliato non va mai online.

Formato di un file  diario/AAAA-MM-GG-titolo-breve.nota

    titolo: Come funzionava il modem a 56k
    data: 2026-11-12
    tipo: passato              (pensiero | cronaca | passato)
    tag: retro, reti           (facoltativo)
    sommario: Una riga ...     (facoltativo)
    bozza: si                  (facoltativo: si = non pubblicato)
    ---
    Un paragrafo. Le righe vicine si uniscono;
    una riga vuota separa i paragrafi.

    # Titoletto
    ## Sotto-titoletto
    > citazione
    - voce di elenco
    ---                        (linea di separazione)
    ```python
    codice copiato così com'è
    ```

    In linea: *grassetto*  _corsivo_  `codice`  [testo](https://indirizzo)
    \\* scrive un asterisco vero. Una riga che finisce con \\ va a capo.
"""

from __future__ import annotations

import datetime
import hashlib
import html
import re
import unicodedata
from dataclasses import dataclass

VERSIONE = 1

TIPI = ("pensiero", "cronaca", "passato")
CHIAVI = ("titolo", "data", "tipo", "tag", "sommario", "bozza")
OBBLIGATORIE = ("titolo", "data", "tipo")

MAX_FILE = 200_000          # byte
MAX_RIGA = 4_000            # caratteri
MAX_TITOLO = 120
MAX_SOMMARIO = 240
MAX_PROFONDITA = 3          # annidamento di *grassetto* e _corsivo_

TAG_AMMESSI = {"p", "h2", "h3", "blockquote", "ul", "li", "hr", "pre", "code",
               "strong", "em", "a", "br", "span"}

_RE_NOME_FILE = re.compile(r"^(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)\.nota$")
_RE_TAG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_RE_LINGUAGGIO = re.compile(r"^[a-z0-9+#.-]{0,20}$")
# solo https, host e percorso con caratteri sicuri (niente virgolette, spazi, < >)
_RE_URL = re.compile(
    r"^https://[A-Za-z0-9](?:[A-Za-z0-9-]{0,62}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,62}[A-Za-z0-9])?)+"
    r"(?::[0-9]{1,5})?"
    r"(?:[/?#][A-Za-z0-9._~:/?#@!$&*+,;=%-]*)?$"
)
_ESCAPABILI = set("\\*_`[]()#>-!")


class ErroreNota(Exception):
    """Errore nel testo di una nota, con file e riga."""

    def __init__(self, file: str, riga: int, messaggio: str):
        super().__init__(f"{file}:{riga}: {messaggio}")
        self.file = file
        self.riga = riga
        self.messaggio = messaggio


@dataclass(frozen=True)
class Nota:
    file: str
    slug: str
    titolo: str
    data: datetime.date
    tipo: str
    tag: tuple
    sommario: str
    bozza: bool
    html: str
    parole: int

    @property
    def hash(self) -> str:
        """Identificativo stabile in stile git (sha1 del nome)."""
        return hashlib.sha1(self.slug.encode("utf-8")).hexdigest()

    @property
    def minuti(self) -> int:
        return max(1, round(self.parole / 200))


def _e(testo: str) -> str:
    return html.escape(testo, quote=True)


# ---------------------------------------------------------------- in linea

def _confine(c: str) -> bool:
    """Vero se il carattere non è una lettera/cifra (inizio/fine di un *marcatore*)."""
    return c == "" or not (c.isalnum() or c == "_")


def _trova_chiusura(s: str, da: int, segno: str) -> int:
    """Indice del segno di chiusura non escapato, seguito da un confine; -1 se assente."""
    i = da
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            i += 2
            continue
        if c == "`":
            fine = s.find("`", i + 1)
            if fine == -1:
                i += 1
                continue
            i = fine + 1
            continue
        if c == segno and i > da and _confine(s[i + 1] if i + 1 < len(s) else ""):
            return i
        i += 1
    return -1


def _in_linea(s: str, file: str, riga: int, prof: int = 0, testo: bool = False,
              link: bool = True) -> str:
    """Converte il testo di una riga. testo=True restituisce testo semplice."""
    fuori = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        prec = s[i - 1] if i > 0 else ""

        if c == "\\":
            if i + 1 < n and s[i + 1] in _ESCAPABILI:
                fuori.append(s[i + 1] if testo else _e(s[i + 1]))
                i += 2
                continue
            fuori.append("\\" if testo else _e("\\"))
            i += 1
            continue

        if c == "`":
            fine = s.find("`", i + 1)
            if fine > i + 1:
                codice = s[i + 1:fine]
                fuori.append(codice if testo else f"<code>{_e(codice)}</code>")
                i = fine + 1
                continue

        if c in "*_" and _confine(prec) and prof < MAX_PROFONDITA:
            fine = _trova_chiusura(s, i + 1, c)
            if fine > i + 1 and not s[i + 1].isspace() and not s[fine - 1].isspace():
                dentro = _in_linea(s[i + 1:fine], file, riga, prof + 1, testo, link)
                if testo:
                    fuori.append(dentro)
                else:
                    tag = "strong" if c == "*" else "em"
                    fuori.append(f"<{tag}>{dentro}</{tag}>")
                i = fine + 1
                continue

        if c == "[" and link:
            chiusa = _trova_chiusura_quadra(s, i + 1)
            if chiusa != -1 and s.startswith("](", chiusa):
                fine_url = s.find(")", chiusa + 2)
                if fine_url == -1:
                    raise ErroreNota(file, riga, "link senza ')' finale")
                url = s[chiusa + 2:fine_url]
                if not _RE_URL.match(url) or len(url) > 2000:
                    raise ErroreNota(file, riga, f"link non valido: «{url[:60]}». "
                                                 "Sono ammessi solo indirizzi https:// completi")
                etichetta = s[i + 1:chiusa]
                if not etichetta.strip():
                    raise ErroreNota(file, riga, "link senza testo tra [ ]")
                dentro = _in_linea(etichetta, file, riga, prof + 1, testo, link=False)
                if testo:
                    fuori.append(dentro)
                else:
                    fuori.append(f'<a href="{_e(url)}" rel="noopener noreferrer external" '
                                 f'target="_blank">{dentro}</a>')
                i = fine_url + 1
                continue

        fuori.append(c if testo else _e(c))
        i += 1
    return "".join(fuori)


def _trova_chiusura_quadra(s: str, da: int) -> int:
    i = da
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            i += 2
            continue
        if s[i] == "[":
            return -1          # niente link dentro i link
        if s[i] == "]":
            return i
        i += 1
    return -1


# ---------------------------------------------------------------- intestazione

def _controlla_caratteri(file: str, righe: list) -> None:
    for n, r in enumerate(righe, 1):
        if len(r) > MAX_RIGA:
            raise ErroreNota(file, n, f"riga troppo lunga (massimo {MAX_RIGA} caratteri)")
        for ch in r:
            cat = unicodedata.category(ch)
            if cat in ("Cc", "Cf", "Cs", "Co", "Cn") and ch != "\t":
                raise ErroreNota(file, n, f"carattere invisibile o non valido U+{ord(ch):04X}")


def _intestazione(file: str, righe: list) -> tuple:
    campi = {}
    for n, r in enumerate(righe, 1):
        if r.strip() == "---":
            return campi, n
        if not r.strip():
            continue
        if ":" not in r:
            raise ErroreNota(file, n, "nell'intestazione ogni riga è 'chiave: valore' "
                                      "(poi una riga con ---)")
        chiave, valore = r.split(":", 1)
        chiave = chiave.strip().lower()
        valore = valore.strip()
        if chiave not in CHIAVI:
            raise ErroreNota(file, n, f"chiave sconosciuta «{chiave}». "
                                      f"Ammesse: {', '.join(CHIAVI)}")
        if chiave in campi:
            raise ErroreNota(file, n, f"chiave «{chiave}» ripetuta")
        campi[chiave] = (valore, n)
    raise ErroreNota(file, len(righe) or 1, "manca la riga --- che chiude l'intestazione")


# ---------------------------------------------------------------- corpo

def _id_titolo(testo: str, usati: set) -> str:
    base = unicodedata.normalize("NFKD", testo).encode("ascii", "ignore").decode()
    base = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")[:50] or "sezione"
    candidato, k = f"s-{base}", 2
    while candidato in usati:
        candidato, k = f"s-{base}-{k}", k + 1
    usati.add(candidato)
    return candidato


def _corpo(file: str, righe: list, inizio: int) -> tuple:
    """Restituisce (html, testo semplice del primo paragrafo, numero di parole)."""
    blocchi = []
    paragrafo, elenco, citazione = [], [], []
    primo = ""
    parole = 0
    usati = set()
    riga_paragrafo = inizio + 1

    def chiudi_paragrafo():
        nonlocal paragrafo, primo
        if not paragrafo:
            return
        parti = []
        for testo_riga, n in paragrafo:
            a_capo = testo_riga.endswith("\\") and not testo_riga.endswith("\\\\")
            if a_capo:
                testo_riga = testo_riga[:-1]
            parti.append(_in_linea(testo_riga.strip(), file, n) + ("<br>" if a_capo else " "))
        blocchi.append("<p>" + "".join(parti).strip() + "</p>")
        if not primo:
            primo = " ".join(_in_linea(t.strip().rstrip("\\"), file, n, testo=True)
                             for t, n in paragrafo)
        paragrafo = []

    def chiudi_elenco():
        nonlocal elenco
        if elenco:
            voci = "".join(f"<li>{_in_linea(t, file, n)}</li>" for t, n in elenco)
            blocchi.append(f"<ul>{voci}</ul>")
            elenco = []

    def chiudi_citazione():
        nonlocal citazione
        if citazione:
            gruppi, corrente = [], []
            for t, n in citazione:
                if t.strip():
                    corrente.append(_in_linea(t.strip(), file, n))
                elif corrente:
                    gruppi.append(corrente)
                    corrente = []
            if corrente:
                gruppi.append(corrente)
            interno = "".join("<p>" + " ".join(g) + "</p>" for g in gruppi)
            blocchi.append(f"<blockquote>{interno}</blockquote>")
            citazione = []

    def chiudi_tutto():
        chiudi_paragrafo()
        chiudi_elenco()
        chiudi_citazione()

    i = 0
    while i < len(righe):
        n = inizio + i + 1
        r = righe[i].replace("\t", "    ").rstrip()
        parole += len(re.findall(r"\w+", r))

        if r.startswith("```"):
            chiudi_tutto()
            lingua = r[3:].strip().lower()
            if not _RE_LINGUAGGIO.match(lingua):
                raise ErroreNota(file, n, "nome del linguaggio non valido dopo ```")
            codice = []
            i += 1
            while i < len(righe) and righe[i].rstrip() != "```":
                codice.append(righe[i].replace("\t", "    ").rstrip())
                i += 1
            if i >= len(righe):
                raise ErroreNota(file, n, "blocco di codice aperto qui e mai chiuso con ```")
            etichetta = f'<span class="nota-lingua">{_e(lingua)}</span>' if lingua else ""
            blocchi.append(f'<pre>{etichetta}<code>{_e(chr(10).join(codice))}</code></pre>')
            i += 1
            continue

        if not r.strip():
            chiudi_paragrafo()
            chiudi_elenco()
            if citazione:
                chiudi_citazione()
            i += 1
            continue

        if r.strip() == "---":
            chiudi_tutto()
            blocchi.append("<hr>")
        elif r.startswith("### "):
            raise ErroreNota(file, n, "titoletti ammessi: '# ' e '## '")
        elif r.startswith("## ") or r.startswith("# "):
            chiudi_tutto()
            livello = "h3" if r.startswith("## ") else "h2"
            testo = r[3:] if livello == "h3" else r[2:]
            if not testo.strip():
                raise ErroreNota(file, n, "titoletto vuoto")
            ident = _id_titolo(_in_linea(testo.strip(), file, n, testo=True), usati)
            blocchi.append(f'<{livello} id="{ident}">{_in_linea(testo.strip(), file, n)}</{livello}>')
        elif r.startswith("> ") or r == ">":
            chiudi_paragrafo()
            chiudi_elenco()
            citazione.append((r[2:] if r.startswith("> ") else "", n))
        elif r.startswith("- "):
            chiudi_paragrafo()
            chiudi_citazione()
            if not r[2:].strip():
                raise ErroreNota(file, n, "voce di elenco vuota")
            elenco.append((r[2:].strip(), n))
        else:
            chiudi_elenco()
            chiudi_citazione()
            if not paragrafo:
                riga_paragrafo = n
            paragrafo.append((r, n))
        i += 1

    chiudi_tutto()
    if not blocchi:
        raise ErroreNota(file, riga_paragrafo, "la nota non ha testo dopo l'intestazione")
    return "\n".join(blocchi), primo, parole


# ---------------------------------------------------------------- ingresso

def leggi(nome_file: str, contenuto: str) -> Nota:
    """Interpreta il testo di una nota. Solleva ErroreNota se qualcosa non va."""
    m = _RE_NOME_FILE.match(nome_file)
    if not m:
        raise ErroreNota(nome_file, 1, "nome file atteso: AAAA-MM-GG-titolo-breve.nota "
                                       "(minuscole, cifre e trattini)")
    if len(contenuto.encode("utf-8")) > MAX_FILE:
        raise ErroreNota(nome_file, 1, "file troppo grande")
    contenuto = contenuto.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    righe = contenuto.split("\n")
    _controlla_caratteri(nome_file, righe)

    campi, fine_testa = _intestazione(nome_file, righe)
    for chiave in OBBLIGATORIE:
        if chiave not in campi:
            raise ErroreNota(nome_file, 1, f"manca «{chiave}:» nell'intestazione")

    titolo, n = campi["titolo"]
    if not titolo or len(titolo) > MAX_TITOLO:
        raise ErroreNota(nome_file, n, f"titolo vuoto o più lungo di {MAX_TITOLO} caratteri")

    valore, n = campi["data"]
    try:
        data = datetime.date.fromisoformat(valore)
    except ValueError:
        raise ErroreNota(nome_file, n, "data non valida, usa AAAA-MM-GG") from None
    if valore != m.group(1):
        raise ErroreNota(nome_file, n, f"la data {valore} non coincide con quella del nome file")

    tipo, n = campi["tipo"]
    if tipo not in TIPI:
        raise ErroreNota(nome_file, n, f"tipo «{tipo}» non valido: usa {', '.join(TIPI)}")

    tag = ()
    if "tag" in campi:
        valore, n = campi["tag"]
        tag = tuple(t.strip() for t in valore.split(",") if t.strip())
        for t in tag:
            if not _RE_TAG.match(t) or len(t) > 30:
                raise ErroreNota(nome_file, n, f"tag «{t}» non valido (minuscole, cifre, trattini)")
        if len(tag) > 8:
            raise ErroreNota(nome_file, n, "al massimo 8 tag")

    bozza = False
    if "bozza" in campi:
        valore, n = campi["bozza"]
        if valore not in ("si", "sì", "no"):
            raise ErroreNota(nome_file, n, "bozza: scrivi si oppure no")
        bozza = valore != "no"

    html_corpo, primo, parole = _corpo(nome_file, righe[fine_testa:], fine_testa)

    if "sommario" in campi:
        sommario, n = campi["sommario"]
        if len(sommario) > MAX_SOMMARIO:
            raise ErroreNota(nome_file, n, f"sommario oltre {MAX_SOMMARIO} caratteri")
    else:
        sommario = primo if len(primo) <= 180 else primo[:177].rsplit(" ", 1)[0] + "…"

    return Nota(file=nome_file, slug=nome_file[:-5], titolo=titolo, data=data,
                tipo=tipo, tag=tag, sommario=sommario, bozza=bozza, html=html_corpo,
                parole=parole)
