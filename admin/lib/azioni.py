"""Le azioni dell'editor, separate dal trasporto HTTP (così si possono provare).

Ogni azione riceve già un utente verificato da accesso.py e restituisce
(stato_http, dizionario) oppure, per i file, (stato_http, bytes, tipo).

Prima di ogni commit il testo passa dallo stesso interprete del sito
(nota.py) e i file da media.py: se la build del sito lo rifiuterebbe,
l'editor lo rifiuta prima, con file, riga e messaggio.
"""

from __future__ import annotations

import base64
import binascii
import urllib.error
import urllib.request
from collections.abc import Mapping

import github
import media
import nota

SITO = "https://mdeangelis.me"
MAX_TESTO = nota.MAX_FILE
MAX_CARICA = 3_000_000          # byte dopo la decodifica: il limite di Vercel è 4,5 MB a richiesta

TIPI_FILE = {"jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp",
             "gif": "image/gif", "mp3": "audio/mpeg", "ogg": "audio/ogg"}

MODELLO = """titolo: {titolo}
data: {data}
ora: {ora}
tipo: pensiero
tag:
sommario:
bozza: si
---
Scrivi qui.
"""


class _MediaPigri(Mapping):
    """I file di diario/media/ come li vuole nota.leggi, letti solo se servono."""

    def __init__(self, nomi):
        self._nomi = set(nomi)
        self._letti = {}

    def __contains__(self, nome):
        return nome in self._nomi

    def __getitem__(self, nome):
        if nome not in self._nomi:
            raise KeyError(nome)
        if nome not in self._letti:
            m = media.prepara(nome, github.leggi(github.percorso_media(nome)))
            self._letti[nome] = (m.tipo, m.larghezza, m.altezza)
        return self._letti[nome]

    def __iter__(self):
        return iter(self._nomi)

    def __len__(self):
        return len(self._nomi)


def intestazione(testo: str) -> dict:
    """Le chiavi dell'intestazione, senza controllarle (serve solo per l'elenco)."""
    campi = {}
    for riga in testo.replace("\r\n", "\n").split("\n")[:20]:
        if riga.strip() == "---":
            break
        chiave, _, valore = riga.partition(":")
        campi[chiave.strip()] = valore.strip()
    return campi


def _bozza(campi: dict) -> bool:
    return campi.get("bozza", "no") in ("si", "sì")


def _errore_nota(err: nota.ErroreNota) -> dict:
    return {"errore": err.messaggio, "riga": err.riga}


def _leggi_nota(nome: str, testo: str):
    nomi_media = [n for n, _, _ in github.elenco("diario/media")]
    return nota.leggi(nome, testo, _MediaPigri(nomi_media))


# ---------------------------------------------------------------- azioni

def elenco_post() -> tuple:
    post = []
    for nome, sha, _ in github.elenco("diario"):
        if not github.RE_POST.match(nome):
            continue
        campi = intestazione(github.leggi(github.percorso_post(nome)).decode("utf-8", "replace"))
        post.append({"nome": nome, "sha": sha, "titolo": campi.get("titolo", nome),
                     "data": campi.get("data", ""), "ora": campi.get("ora", ""),
                     "tipo": campi.get("tipo", ""), "bozza": _bozza(campi)})
    post.sort(key=lambda p: (p["data"], p["ora"], p["nome"]), reverse=True)
    media_ = [{"nome": n, "dimensione": d} for n, _, d in github.elenco("diario/media")
              if github.RE_MEDIA.match(n)]
    return 200, {"post": post, "media": media_}


def apri_post(nome: str) -> tuple:
    percorso = github.percorso_post(nome)
    sha = next((s for n, s, _ in github.elenco("diario") if n == nome), None)
    if sha is None:
        return 404, {"errore": "post non trovato"}
    return 200, {"nome": nome, "sha": sha, "testo": github.leggi(percorso).decode("utf-8")}


def nuovo(titolo: str, data: str, ora: str) -> tuple:
    """Solo il testo di partenza: niente viene salvato finché non premi Salva."""
    return 200, {"testo": MODELLO.format(titolo=titolo or "Senza titolo", data=data, ora=ora)}


def _controlla_testo(nome, testo):
    github.percorso_post(nome)
    if not isinstance(testo, str) or len(testo.encode("utf-8")) > MAX_TESTO:
        raise ValueError("testo assente o troppo lungo")


def anteprima(nome: str, testo: str) -> tuple:
    _controlla_testo(nome, testo)
    try:
        n = _leggi_nota(nome, testo)
    except nota.ErroreNota as err:
        return 200, {"ok": False, **_errore_nota(err)}
    except media.ErroreMedia as err:
        return 200, {"ok": False, "errore": str(err), "riga": 0}
    return 200, {"ok": True, "html": n.html, "titolo": n.titolo, "data": n.data.isoformat(),
                 "ora": n.ora, "tipo": n.tipo, "tag": list(n.tag), "sommario": n.sommario,
                 "bozza": n.bozza, "copertina": n.copertina, "minuti": n.minuti}


def salva(nome: str, testo: str, sha, email: str) -> tuple:
    _controlla_testo(nome, testo)
    if sha is not None and (not isinstance(sha, str) or len(sha) != 40):
        raise ValueError("versione non valida")
    try:
        n = _leggi_nota(nome, testo)
    except nota.ErroreNota as err:
        return 422, {"ok": False, **_errore_nota(err)}
    except media.ErroreMedia as err:
        return 422, {"ok": False, "errore": str(err), "riga": 0}

    esistenti = {nm: s for nm, s, _ in github.elenco("diario") if github.RE_POST.match(nm)}
    if sha is None and nome in esistenti:
        return 409, {"ok": False, "errore": "esiste già un post con questo nome", "riga": 1}
    if sha is not None and esistenti.get(nome) != sha:
        return 409, {"ok": False, "errore": "il post è cambiato nel frattempo: ricarica e riprova",
                     "riga": 0}

    # Le stesse regole della build: i link ad altri post devono portare a post che
    # esistono, e un post pubblicato non può puntare a una bozza (né diventarlo
    # se altri post pubblicati lo citano).
    for altro, riga in n.collegamenti:
        file_altro = altro + ".nota"
        if file_altro not in esistenti and file_altro != nome:
            return 422, {"ok": False, "errore": "il post " + altro + " non esiste", "riga": riga}
        if not n.bozza and file_altro != nome:
            campi = intestazione(github.leggi(github.percorso_post(file_altro)).decode("utf-8", "replace"))
            if _bozza(campi):
                return 422, {"ok": False, "errore": "il post " + altro + " è ancora una bozza",
                             "riga": riga}
    if n.bozza and nome in esistenti:
        citazione = "(/diario/" + n.slug + "/"
        for altro in esistenti:
            if altro == nome:
                continue
            t = github.leggi(github.percorso_post(altro)).decode("utf-8", "replace")
            if citazione in t and not _bozza(intestazione(t)):
                return 422, {"ok": False, "riga": 0, "errore": "il post pubblicato " + altro[:-5]
                             + " ha un link a questo: non può tornare bozza"}

    azione = "aggiorna" if sha else "nuovo post"
    messaggio = ("Diario: " + azione + " «" + n.titolo + "» (dall'editor)\n\n"
                 + ("Bozza: non pubblicato." if n.bozza else "Pubblicato."))
    nuovo_sha = github.scrivi(github.percorso_post(nome), testo.replace("\r\n", "\n").encode("utf-8"),
                              messaggio, sha)
    return 200, {"ok": True, "sha": nuovo_sha, "bozza": n.bozza,
                 "indirizzo": SITO + "/diario/" + n.slug + "/"}


def carica(nome: str, dati_b64: str) -> tuple:
    percorso = github.percorso_media(nome)
    if not isinstance(dati_b64, str) or len(dati_b64) > MAX_CARICA * 4 // 3 + 8:
        return 413, {"ok": False, "errore": "file troppo grande per il caricamento (massimo 3 MB)"}
    try:
        dati = base64.b64decode(dati_b64, validate=True)
    except (binascii.Error, ValueError):
        return 400, {"ok": False, "errore": "file non leggibile"}
    try:
        m = media.prepara(nome, dati)
    except media.ErroreMedia as err:
        return 422, {"ok": False, "errore": err.messaggio}
    if any(n == nome for n, _, _ in github.elenco("diario/media")):
        return 409, {"ok": False, "errore": "esiste già un file con questo nome: scegline un altro"}
    # nel repository va la copia già ripulita: posizione e dati del telefono non ci arrivano mai
    github.scrivi(percorso, m.dati, "Diario: aggiunge " + nome + " (dall'editor)")
    return 200, {"ok": True, "nome": nome, "tipo": m.tipo, "larghezza": m.larghezza,
                 "altezza": m.altezza, "dimensione": len(m.dati)}


def file_media(nome: str) -> tuple:
    m = media.prepara(nome, github.leggi(github.percorso_media(nome)))
    return 200, m.dati, TIPI_FILE[m.formato]


def stato_pubblicazione(nome: str) -> tuple:
    """Il post è già online? (la build di Vercel richiede circa un minuto)"""
    github.percorso_post(nome)
    url = SITO + "/diario/" + nome[:-5] + "/"
    richiesta = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "admin-mdeangelis"})
    try:
        with urllib.request.urlopen(richiesta, timeout=5) as r:
            online = r.status == 200
    except (urllib.error.URLError, TimeoutError):
        online = False
    return 200, {"online": online, "indirizzo": url}
