"""Nota: il linguaggio del diario di mdeangelis.me (versione 2).

Scritto da zero, solo libreria standard di Python. Gira soltanto quando si
generano le pagine: sul sito arriva HTML statico, mai codice eseguibile.

Regole di sicurezza
- Niente HTML scritto a mano: tutto il testo viene sempre "escapato".
- L'interprete produce solo i tag e gli attributi di una lista chiusa
  (vedi ATTRIBUTI).
- Link: solo https:// completi, pagine del sito (/...) o sezioni (#...).
  I link ad altri post e alle sezioni vengono controllati: se non esistono,
  la pubblicazione si ferma.
- Immagini e audio: solo file di diario/media/ già controllati da media.py.
- Qualsiasi errore ferma la generazione con file e numero di riga:
  un post sbagliato non va mai online.

La guida completa, con esempi, è in diario/COME-SI-SCRIVE.md.
"""

from __future__ import annotations

import datetime
import hashlib
import html
import re
import unicodedata
from dataclasses import dataclass

VERSIONE = 2

TIPI = ("pensiero", "cronaca", "passato")
CHIAVI = ("titolo", "data", "ora", "tipo", "tag", "sommario", "copertina", "bozza")
OBBLIGATORIE = ("titolo", "data", "tipo")

MAX_FILE = 200_000          # byte
MAX_RIGA = 4_000            # caratteri
MAX_TITOLO = 120
MAX_SOMMARIO = 240
MAX_PROFONDITA = 3          # annidamento di *grassetto*, _corsivo_, ~~barrato~~...
MAX_COLONNE = 10

PERCORSO_MEDIA = "/diario/media/"

# Tutto l'HTML che l'interprete può produrre: tag -> attributi ammessi.
ATTRIBUTI = {
    "p": {"class"}, "h2": {"id"}, "h3": {"id"}, "blockquote": set(), "hr": set(),
    "ul": set(), "ol": {"start"}, "li": {"id"},
    "pre": set(), "code": set(), "strong": set(), "em": set(), "del": set(),
    "mark": set(), "kbd": set(), "sup": {"class"}, "br": set(), "span": {"class"},
    "a": {"href", "rel", "target", "id", "class", "aria-label"},
    "figure": {"class"}, "figcaption": set(), "div": {"class"},
    "img": {"src", "alt", "width", "height", "loading", "decoding"},
    "audio": {"src", "controls", "preload"},
    "table": set(), "thead": set(), "tbody": set(), "tr": set(), "th": {"class"}, "td": {"class"},
    "aside": {"class"}, "section": {"class", "aria-label"},
}
TAG_AMMESSI = set(ATTRIBUTI)
CLASSI = {"nota-lingua", "spunta", "spunta-si", "riquadro", "riquadro-tipo", "r-nota",
          "r-consiglio", "r-attenzione", "r-curiosita", "galleria", "tabella", "nota-img",
          "nota-audio", "apri", "rimando", "note-piede", "torna", "a-c", "a-d"}

# [!tipo] all'inizio di una citazione -> (classe, etichetta)
RIQUADRI = {"nota": ("r-nota", "nota"), "consiglio": ("r-consiglio", "consiglio"),
            "attenzione": ("r-attenzione", "attenzione"),
            "curiosita": ("r-curiosita", "curiosità"), "curiosità": ("r-curiosita", "curiosità")}

_RE_NOME_FILE = re.compile(r"^(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)\.nota$")
_RE_ORA = re.compile(r"^([01][0-9]|2[0-3]):[0-5][0-9]$")
_RE_TAG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_RE_LINGUAGGIO = re.compile(r"^[a-z0-9+#.-]{0,20}$")
# solo https, host e percorso con caratteri sicuri (niente virgolette, spazi, < >)
_RE_URL = re.compile(
    r"^https://[A-Za-z0-9](?:[A-Za-z0-9-]{0,62}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,62}[A-Za-z0-9])?)+"
    r"(?::[0-9]{1,5})?"
    r"(?:[/?#][A-Za-z0-9._~:/?#@!$&*+,;=%-]*)?$"
)
# pagine del sito: /diario/, /#musica ... mai // (altro sito) né ..
_RE_INTERNO = re.compile(r"^/(?:[a-z0-9_-]+(?:[./][a-z0-9_-]+)*/?)?(?:#[a-z0-9-]+)?$")
_RE_POST = re.compile(r"^/diario/(\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*)/(?:#[a-z0-9-]+)?$")
_RE_ANCORA = re.compile(r"^#[a-z0-9][a-z0-9-]{0,80}$")
_RE_NOME_MEDIA = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}\.[a-z0-9]{2,4}$")
_RE_MEDIA = re.compile(r'^!\[([^\]]*)\]\(([^)\s"]+)(?:\s+"([^"]*)")?\)$')
_RE_NUMERATO = re.compile(r"^(\d{1,3})\. (.*)$")
_RE_SPUNTA = re.compile(r"^\[([ xX])\] (.+)$")
_RE_DEF_NOTA = re.compile(r"^\[\^([a-z0-9-]{1,20})\]:(.*)$")
_RE_RIF_NOTA = re.compile(r"\[\^([a-z0-9-]{1,20})\]")
_RE_SEPARATORE = re.compile(r"^\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)*\|?$")
_RE_RIQUADRO = re.compile(r"^\[!([^\]]+)\]$")
_ESCAPABILI = set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")   # tutta la punteggiatura ASCII


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
    copertina: str = ""          # nome del file in diario/media/
    media: tuple = ()            # file di diario/media/ usati dal post
    collegamenti: tuple = ()     # (slug di un altro post, riga)
    ora: str = ""                # HH:MM, ora italiana; ordina i post dello stesso giorno

    @property
    def hash(self) -> str:
        """Identificativo stabile in stile git (sha1 del nome)."""
        return hashlib.sha1(self.slug.encode("utf-8")).hexdigest()

    @property
    def minuti(self) -> int:
        return max(1, round(self.parole / 200))


def _e(testo: str) -> str:
    return html.escape(testo, quote=True)


class _Contesto:
    """Quello che serve ricordare mentre si legge una nota."""

    def __init__(self, file: str, media):
        self.file = file
        self.media = media          # nome -> (tipo, larghezza, altezza), o None
        self.note = {}              # etichetta -> (testo, riga)
        self.ordine = []            # etichette nell'ordine del primo rimando
        self.conta = {}             # etichetta -> rimandi già scritti
        self.ancore = []            # (ancora, riga)
        self.ids = set()            # id dei titoletti
        self.collegamenti = []      # (slug, riga)
        self.usati = []             # file di media usati

    def errore(self, riga: int, messaggio: str) -> ErroreNota:
        return ErroreNota(self.file, riga, messaggio)

    def rimando(self, etichetta: str, riga: int) -> str:
        if etichetta not in self.note:
            raise self.errore(riga, f"la nota [^{etichetta}] non è definita: aggiungi "
                                    f"una riga «[^{etichetta}]: testo della nota»")
        if etichetta not in self.ordine:
            self.ordine.append(etichetta)
        numero = self.ordine.index(etichetta) + 1
        self.conta[etichetta] = self.conta.get(etichetta, 0) + 1
        return (f'<sup class="rimando"><a href="#nota-{etichetta}" '
                f'id="rif-{etichetta}-{self.conta[etichetta]}">[{numero}]</a></sup>')

    def collega(self, url: str, riga: int) -> tuple:
        """Controlla un link; restituisce (indirizzo, esterno)."""
        if url.startswith("https://") and _RE_URL.match(url) and len(url) <= 2000:
            return url, True
        if _RE_ANCORA.match(url):
            self.ancore.append((url[1:], riga))
            return url, False
        if _RE_INTERNO.match(url) and len(url) <= 300:
            post = _RE_POST.match(url)
            if post and (post.group(1), riga) not in self.collegamenti:
                self.collegamenti.append((post.group(1), riga))
            return url, False
        raise self.errore(riga, f"link non valido: «{url[:60]}». Sono ammessi indirizzi "
                                "https:// completi, pagine del sito (/diario/...) e sezioni (#...)")

    def medium(self, nome: str, riga: int) -> tuple:
        if not _RE_NOME_MEDIA.match(nome) or self.media is None or nome not in self.media:
            raise self.errore(riga, f"file «{nome[:60]}» non trovato in diario/media/")
        if nome not in self.usati:
            self.usati.append(nome)
        return self.media[nome]


# ---------------------------------------------------------------- in linea

def _confine(c: str) -> bool:
    """Vero se il carattere non è una lettera/cifra (inizio/fine di un *marcatore*)."""
    return c == "" or not (c.isalnum() or c == "_")


def _trova_chiusura(s: str, da: int, segno: str) -> int:
    """Indice del segno di chiusura non escapato, seguito da un confine; -1 se assente.
    Il segno può essere di uno o due caratteri (* oppure ~~)."""
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
        dopo = i + len(segno)
        if s.startswith(segno, i) and i > da and _confine(s[dopo] if dopo < len(s) else ""):
            return i
        i += 1
    return -1


def _in_linea(s: str, ctx: _Contesto, riga: int, prof: int = 0, testo: bool = False,
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

        # ~~barrato~~, ==evidenziato== e **grassetto** (come *grassetto*, per chi viene dal Markdown)
        if c in "~=*" and s.startswith(c * 2, i) and _confine(prec) and prof < MAX_PROFONDITA:
            fine = _trova_chiusura(s, i + 2, c * 2)
            if fine > i + 2 and not s[i + 2].isspace() and not s[fine - 1].isspace():
                dentro = _in_linea(s[i + 2:fine], ctx, riga, prof + 1, testo, link)
                tag = {"~": "del", "=": "mark", "*": "strong"}[c]
                fuori.append(dentro if testo else f"<{tag}>{dentro}</{tag}>")
                i = fine + 2
                continue

        # *grassetto* e _corsivo_
        if c in "*_" and _confine(prec) and prof < MAX_PROFONDITA:
            fine = _trova_chiusura(s, i + 1, c)
            if fine > i + 1 and not s[i + 1].isspace() and not s[fine - 1].isspace():
                dentro = _in_linea(s[i + 1:fine], ctx, riga, prof + 1, testo, link)
                tag = "strong" if c == "*" else "em"
                fuori.append(dentro if testo else f"<{tag}>{dentro}</{tag}>")
                i = fine + 1
                continue

        # [[Ctrl]]: un tasto della tastiera
        if c == "[" and s.startswith("[[", i):
            fine = s.find("]]", i + 2)
            tasto = s[i + 2:fine] if fine != -1 else ""
            if tasto and len(tasto) <= 30 and tasto.strip() == tasto and "[" not in tasto:
                fuori.append(tasto if testo else f"<kbd>{_e(tasto)}</kbd>")
                i = fine + 2
                continue

        # [^1]: rimando a una nota a piè di pagina
        if c == "[" and s.startswith("[^", i):
            m = _RE_RIF_NOTA.match(s, i)
            if m:
                if not testo:
                    fuori.append(ctx.rimando(m.group(1), riga))
                i = m.end()
                continue

        # [testo](indirizzo)
        if c == "[" and link:
            chiusa = _trova_chiusura_quadra(s, i + 1)
            if chiusa != -1 and s.startswith("](", chiusa):
                if prec == "!" and not (i >= 2 and s[i - 2] == "\\"):
                    raise ctx.errore(riga, "immagini e audio vanno su una riga da sole: "
                                           "![descrizione](file.jpg)")
                fine_url = s.find(")", chiusa + 2)
                if fine_url == -1:
                    raise ctx.errore(riga, "link senza ')' finale")
                url, esterno = ctx.collega(s[chiusa + 2:fine_url], riga)
                etichetta = s[i + 1:chiusa]
                if not etichetta.strip():
                    raise ctx.errore(riga, "link senza testo tra [ ]")
                dentro = _in_linea(etichetta, ctx, riga, prof + 1, testo, link=False)
                if testo:
                    fuori.append(dentro)
                elif esterno:
                    fuori.append(f'<a href="{_e(url)}" rel="noopener noreferrer external" '
                                 f'target="_blank">{dentro}</a>')
                else:
                    fuori.append(f'<a href="{_e(url)}">{dentro}</a>')
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


def _celle(riga: str) -> list:
    """Divide una riga di tabella sulle | non escapate e non dentro `codice`."""
    s = riga.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    celle, corrente, i, codice = [], [], 0, False
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s):
            corrente.append(s[i:i + 2])
            i += 2
            continue
        if ch == "`":
            codice = not codice
        if ch == "|" and not codice:
            celle.append("".join(corrente).strip())
            corrente = []
        else:
            corrente.append(ch)
        i += 1
    celle.append("".join(corrente).strip())
    return celle


def _corpo(ctx: _Contesto, righe: list, inizio: int) -> tuple:
    """Restituisce (html, testo semplice del primo paragrafo, numero di parole)."""
    file = ctx.file
    blocchi = []
    paragrafo, citazione, tabella, immagini = [], [], [], []
    elenco = []           # [(tipo "ul"/"ol", testo, riga)]
    primo = ""
    parole = 0
    riga_paragrafo = inizio + 1

    # Prima passata: le definizioni delle note a piè di pagina, ovunque siano.
    definizioni = set()
    dentro_codice = False
    for k, r in enumerate(righe):
        if r.startswith("```"):
            dentro_codice = not dentro_codice
            continue
        m = None if dentro_codice else _RE_DEF_NOTA.match(r)
        if m:
            etichetta, testo = m.group(1), m.group(2).strip()
            if etichetta in ctx.note:
                raise ctx.errore(inizio + k + 1, f"nota [^{etichetta}] definita due volte")
            if not testo:
                raise ctx.errore(inizio + k + 1, f"la nota [^{etichetta}] è vuota")
            ctx.note[etichetta] = (testo, inizio + k + 1)
            definizioni.add(k)

    def chiudi_paragrafo():
        nonlocal paragrafo, primo
        if not paragrafo:
            return
        parti = []
        for testo_riga, n in paragrafo:
            a_capo = testo_riga.endswith("\\") and not testo_riga.endswith("\\\\")
            if a_capo:
                testo_riga = testo_riga[:-1]
            parti.append(_in_linea(testo_riga.strip(), ctx, n) + ("<br>" if a_capo else " "))
        blocchi.append("<p>" + "".join(parti).strip() + "</p>")
        if not primo:
            primo = " ".join(_in_linea(t.strip().rstrip("\\"), ctx, n, testo=True)
                             for t, n in paragrafo)
        paragrafo = []

    def voce(testo: str, n: int) -> str:
        m = _RE_SPUNTA.match(testo)
        if m:
            fatto = m.group(1) != " "
            classe = "spunta spunta-si" if fatto else "spunta"
            return (f'<li><span class="{classe}">[{"x" if fatto else " "}]</span> '
                    f'{_in_linea(m.group(2), ctx, n)}</li>')
        return f"<li>{_in_linea(testo, ctx, n)}</li>"

    def chiudi_elenco():
        nonlocal elenco
        if elenco:
            tipo = elenco[0][0]
            voci = "".join(voce(t, n) for _, t, n, _r in elenco)
            inizio_ol = ""
            if tipo == "ol":
                partenza = int(_RE_NUMERATO.match(elenco[0][3]).group(1))
                inizio_ol = f' start="{partenza}"' if partenza != 1 else ""
            blocchi.append(f"<{tipo}{inizio_ol}>{voci}</{tipo}>")
            elenco = []

    def chiudi_citazione():
        nonlocal citazione
        if not citazione:
            return
        riquadro = None
        if citazione[0][0].strip():
            m = _RE_RIQUADRO.match(citazione[0][0].strip())
            if m:
                tipo = m.group(1).lower()
                if tipo not in RIQUADRI:
                    raise ctx.errore(citazione[0][1], f"riquadro «{tipo}» sconosciuto: usa "
                                                      "[!nota], [!consiglio], [!attenzione] o [!curiosita]")
                riquadro = RIQUADRI[tipo]
                prima = citazione[0][1]
                citazione = citazione[1:]
                if not any(t.strip() for t, _ in citazione):
                    raise ctx.errore(prima, "riquadro vuoto: scrivi il testo nelle righe '> ' sotto")
        gruppi, corrente = [], []
        for t, n in citazione:
            if t.strip():
                corrente.append(_in_linea(t.strip(), ctx, n))
            elif corrente:
                gruppi.append(corrente)
                corrente = []
        if corrente:
            gruppi.append(corrente)
        interno = "".join("<p>" + " ".join(g) + "</p>" for g in gruppi)
        if riquadro:
            classe, etichetta = riquadro
            blocchi.append(f'<aside class="riquadro {classe}"><p class="riquadro-tipo">'
                           f'[ {etichetta} ]</p>{interno}</aside>')
        else:
            blocchi.append(f"<blockquote>{interno}</blockquote>")
        citazione = []

    def chiudi_tabella():
        nonlocal tabella
        if not tabella:
            return
        if len(tabella) < 2 or not _RE_SEPARATORE.match(tabella[1][0].strip()):
            raise ctx.errore(tabella[0][1], "tabella: la seconda riga deve essere il "
                                            "separatore, per esempio |---|---|")
        testata = _celle(tabella[0][0])
        allinea = []
        for parte in _celle(tabella[1][0]):
            if parte.startswith(":") and parte.endswith(":"):
                allinea.append(' class="a-c"')
            elif parte.endswith(":"):
                allinea.append(' class="a-d"')
            else:
                allinea.append("")
        colonne = len(testata)
        if colonne > MAX_COLONNE:
            raise ctx.errore(tabella[0][1], f"tabella: al massimo {MAX_COLONNE} colonne")
        if len(allinea) != colonne:
            raise ctx.errore(tabella[1][1], f"tabella: il separatore ha {len(allinea)} colonne, "
                                            f"l'intestazione {colonne}")
        n0 = tabella[0][1]
        th = "".join(f"<th{a}>{_in_linea(c, ctx, n0)}</th>" for c, a in zip(testata, allinea))
        corpo = []
        for riga_t, n in tabella[2:]:
            celle = _celle(riga_t)
            if len(celle) != colonne:
                raise ctx.errore(n, f"tabella: questa riga ha {len(celle)} colonne invece di {colonne}")
            corpo.append("<tr>" + "".join(f"<td{a}>{_in_linea(c, ctx, n)}</td>"
                                          for c, a in zip(celle, allinea)) + "</tr>")
        blocchi.append(f'<div class="tabella"><table><thead><tr>{th}</tr></thead>'
                       f'<tbody>{"".join(corpo)}</tbody></table></div>')
        tabella = []

    def chiudi_immagini():
        nonlocal immagini
        if len(immagini) == 1:
            blocchi.append(immagini[0])
        elif immagini:
            blocchi.append('<div class="galleria">' + "".join(immagini) + "</div>")
        immagini = []

    def chiudi_tutto(tranne: str = ""):
        if tranne != "paragrafo":
            chiudi_paragrafo()
        if tranne != "elenco":
            chiudi_elenco()
        if tranne != "citazione":
            chiudi_citazione()
        if tranne != "tabella":
            chiudi_tabella()
        if tranne != "immagini":
            chiudi_immagini()

    def media(r: str, n: int):
        m = _RE_MEDIA.match(r.strip())
        if not m:
            raise ctx.errore(n, 'immagine o audio scritto male: usa ![descrizione](file.jpg) '
                                'oppure ![descrizione](file.jpg "didascalia")')
        alt_grezzo, nome, didascalia = m.groups()
        tipo, larghezza, altezza = ctx.medium(nome, n)
        alt = _in_linea(alt_grezzo.strip(), ctx, n, testo=True, link=False).strip()
        if not alt:
            raise ctx.errore(n, "scrivi tra [ ] cosa si vede (o si sente): serve a chi non vede "
                                "l'immagine")
        sotto = _in_linea(didascalia.strip(), ctx, n) if didascalia and didascalia.strip() else ""
        src = _e(PERCORSO_MEDIA + nome)
        if tipo == "audio":
            chiudi_tutto()
            titolo = _e(alt) + (f" <span>{sotto}</span>" if sotto else "")
            blocchi.append(f'<figure class="nota-audio"><figcaption>{titolo}</figcaption>'
                           f'<audio controls preload="none" src="{src}"></audio></figure>')
        else:
            chiudi_tutto(tranne="immagini")
            cap = f"<figcaption>{sotto}</figcaption>" if sotto else ""
            immagini.append(f'<figure class="nota-img"><a class="apri" href="{src}">'
                            f'<img src="{src}" alt="{_e(alt)}" width="{int(larghezza)}" '
                            f'height="{int(altezza)}" loading="lazy" decoding="async"></a>{cap}</figure>')

    i = 0
    while i < len(righe):
        n = inizio + i + 1
        r = righe[i].replace("\t", "    ").rstrip()
        parole += len(re.findall(r"\w+", r))

        if i in definizioni:
            chiudi_tutto()
            i += 1
            continue

        if r.startswith("```"):
            chiudi_tutto()
            lingua = r[3:].strip().lower()
            if not _RE_LINGUAGGIO.match(lingua):
                raise ctx.errore(n, "nome del linguaggio non valido dopo ```")
            codice = []
            i += 1
            while i < len(righe) and righe[i].rstrip() != "```":
                codice.append(righe[i].replace("\t", "    ").rstrip())
                i += 1
            if i >= len(righe):
                raise ctx.errore(n, "blocco di codice aperto qui e mai chiuso con ```")
            etichetta = f'<span class="nota-lingua">{_e(lingua)}</span>' if lingua else ""
            blocchi.append(f'<pre>{etichetta}<code>{_e(chr(10).join(codice))}</code></pre>')
            i += 1
            continue

        if not r.strip():
            chiudi_tutto()
            i += 1
            continue

        numerato = _RE_NUMERATO.match(r)
        if r.strip() == "---":
            chiudi_tutto()
            blocchi.append("<hr>")
        elif r.startswith("### "):
            raise ctx.errore(n, "titoletti ammessi: '# ' e '## '")
        elif r.startswith("## ") or r.startswith("# "):
            chiudi_tutto()
            livello = "h3" if r.startswith("## ") else "h2"
            testo = r[3:] if livello == "h3" else r[2:]
            if not testo.strip():
                raise ctx.errore(n, "titoletto vuoto")
            ident = _id_titolo(_in_linea(testo.strip(), ctx, n, testo=True), ctx.ids)
            blocchi.append(f'<{livello} id="{ident}">{_in_linea(testo.strip(), ctx, n)}</{livello}>')
        elif r.startswith("!["):
            media(r, n)
        elif r.startswith("> ") or r == ">":
            chiudi_tutto(tranne="citazione")
            citazione.append((r[2:] if r.startswith("> ") else "", n))
        elif r.startswith("|"):
            chiudi_tutto(tranne="tabella")
            tabella.append((r, n))
        elif r.startswith("- ") or numerato:
            chiudi_tutto(tranne="elenco")
            tipo = "ol" if numerato else "ul"
            testo = (numerato.group(2) if numerato else r[2:]).strip()
            if not testo:
                raise ctx.errore(n, "voce di elenco vuota")
            if elenco and elenco[0][0] != tipo:
                chiudi_elenco()
            elenco.append((tipo, testo, n, r))
        else:
            chiudi_tutto(tranne="paragrafo")
            if not paragrafo:
                riga_paragrafo = n
            paragrafo.append((r, n))
        i += 1

    chiudi_tutto()
    if not blocchi:
        raise ctx.errore(riga_paragrafo, "la nota non ha testo dopo l'intestazione")

    # Note a piè di pagina, nell'ordine in cui sono richiamate.
    if ctx.ordine:
        voci, j = [], 0
        while j < len(ctx.ordine):          # una nota può richiamarne un'altra
            etichetta = ctx.ordine[j]
            testo, rn = ctx.note[etichetta]
            voci.append(f'<li id="nota-{etichetta}">{_in_linea(testo, ctx, rn)} '
                        f'<a class="torna" href="#rif-{etichetta}-1" aria-label="torna al testo">↑</a></li>')
            j += 1
        blocchi.append('<section class="note-piede" aria-label="Note"><ol>'
                       + "".join(voci) + "</ol></section>")
    for etichetta, (_, rn) in ctx.note.items():
        if etichetta not in ctx.ordine:
            raise ctx.errore(rn, f"la nota [^{etichetta}] non è mai richiamata nel testo")

    esistenti = ctx.ids | {f"nota-{k}" for k in ctx.ordine}
    for ancora, rn in ctx.ancore:
        if ancora not in esistenti:
            raise ctx.errore(rn, f"il link #{ancora} non porta a nessuna sezione di questo post")

    return "\n".join(blocchi), primo, parole


# ---------------------------------------------------------------- ingresso

def leggi(nome_file: str, contenuto: str, media=None) -> Nota:
    """Interpreta il testo di una nota. Solleva ErroreNota se qualcosa non va.

    media: dizionario nome file -> (tipo, larghezza, altezza) dei file di
    diario/media/ già controllati (vedi media.py). Senza, immagini e audio
    danno errore."""
    m = _RE_NOME_FILE.match(nome_file)
    if not m:
        raise ErroreNota(nome_file, 1, "nome file atteso: AAAA-MM-GG-titolo-breve.nota "
                                       "(minuscole, cifre e trattini)")
    if len(contenuto.encode("utf-8")) > MAX_FILE:
        raise ErroreNota(nome_file, 1, "file troppo grande")
    contenuto = contenuto.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    righe = contenuto.split("\n")
    _controlla_caratteri(nome_file, righe)
    ctx = _Contesto(nome_file, media)

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

    ora = ""
    if "ora" in campi:
        ora, n = campi["ora"]
        if not _RE_ORA.match(ora):
            raise ErroreNota(nome_file, n, "ora non valida, usa HH:MM (per esempio 21:30)")

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

    copertina = ""
    if "copertina" in campi:
        copertina, n = campi["copertina"]
        if ctx.medium(copertina, n)[0] != "immagine":
            raise ErroreNota(nome_file, n, "la copertina deve essere un'immagine")

    html_corpo, primo, parole = _corpo(ctx, righe[fine_testa:], fine_testa)

    if "sommario" in campi:
        sommario, n = campi["sommario"]
        if len(sommario) > MAX_SOMMARIO:
            raise ErroreNota(nome_file, n, f"sommario oltre {MAX_SOMMARIO} caratteri")
    else:
        sommario = primo if len(primo) <= 180 else primo[:177].rsplit(" ", 1)[0] + "…"

    return Nota(file=nome_file, slug=nome_file[:-5], titolo=titolo, data=data,
                tipo=tipo, tag=tag, sommario=sommario, bozza=bozza, html=html_corpo,
                parole=parole, copertina=copertina, media=tuple(ctx.usati),
                collegamenti=tuple(ctx.collegamenti), ora=ora)
