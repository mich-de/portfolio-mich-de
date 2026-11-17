"""Lettura e scrittura dei file del sito sul repository GitHub.

L'editor non salva niente da sé: ogni modifica diventa un commit su main,
e la build di Vercel del sito (test + genera.py) fa il resto.

La chiave è una "fine-grained token" con il solo permesso Contents
(lettura e scrittura) sul solo repository del sito, nella variabile
GITHUB_TOKEN di Vercel. Non esce mai da qui: niente log, niente risposte.

Si possono toccare solo due tipi di percorso, controllati qui sotto:
diario/<nome>.nota e diario/media/<nome>.
"""

from __future__ import annotations

import base64
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

REPO = os.environ.get("GITHUB_REPO", "mich-de/portfolio-mich-de")
RAMO = os.environ.get("GITHUB_BRANCH", "main")
API = "https://api.github.com"

RE_POST = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*(?:\.en)?\.nota$")
RE_MEDIA = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}\.(jpg|jpeg|png|webp|gif|mp3|ogg)$")


class ErroreGitHub(Exception):
    def __init__(self, stato: int, messaggio: str):
        super().__init__(messaggio)
        self.stato = stato


def percorso_post(nome: str) -> str:
    if not isinstance(nome, str) or not RE_POST.match(nome):
        raise ErroreGitHub(400, "nome del post non valido")
    return "diario/" + nome


def percorso_media(nome: str) -> str:
    if not isinstance(nome, str) or not RE_MEDIA.match(nome):
        raise ErroreGitHub(400, "nome del file non valido")
    return "diario/media/" + nome


def _chiave() -> str:
    chiave = os.environ.get("GITHUB_TOKEN", "")
    if not chiave:
        raise ErroreGitHub(503, "manca la chiave GitHub nelle impostazioni di Vercel")
    return chiave


def _chiama(metodo: str, percorso: str, corpo=None, grezzo: bool = False):
    url = API + "/repos/" + REPO + "/contents/" + urllib.parse.quote(percorso)
    if metodo == "GET":
        url += "?ref=" + urllib.parse.quote(RAMO)
    intestazioni = {
        "Authorization": "Bearer " + _chiave(),
        "Accept": "application/vnd.github.raw" if grezzo else "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "admin-mdeangelis",
    }
    dati = None
    if corpo is not None:
        dati = json.dumps(corpo).encode("utf-8")
        intestazioni["Content-Type"] = "application/json"
    richiesta = urllib.request.Request(url, data=dati, method=metodo, headers=intestazioni)
    try:
        with urllib.request.urlopen(richiesta, timeout=20) as r:
            testo = r.read(40_000_000)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            raise ErroreGitHub(404, "file non trovato") from None
        if err.code in (409, 422):
            raise ErroreGitHub(409, "il file è cambiato nel frattempo: ricarica e riprova") from None
        if err.code in (401, 403):
            raise ErroreGitHub(502, "GitHub ha rifiutato la chiave: controlla che sia valida "
                                    "e abbia il permesso Contents in scrittura") from None
        raise ErroreGitHub(502, "GitHub non risponde come previsto (" + str(err.code) + ")") from None
    except (urllib.error.URLError, TimeoutError):
        raise ErroreGitHub(502, "GitHub non raggiungibile, riprova tra poco") from None
    return testo if grezzo else json.loads(testo.decode("utf-8"))


def elenco(cartella: str) -> list:
    """[(nome, sha, dimensione)] dei file di una cartella."""
    if cartella not in ("diario", "diario/media"):
        raise ErroreGitHub(400, "cartella non ammessa")
    try:
        voci = _chiama("GET", cartella)
    except ErroreGitHub as err:
        if err.stato == 404:
            return []
        raise
    return [(v["name"], v["sha"], v.get("size", 0)) for v in voci if v.get("type") == "file"]


def leggi(percorso: str) -> bytes:
    return _chiama("GET", percorso, grezzo=True)


def scrivi(percorso: str, dati: bytes, messaggio: str, sha: str = None) -> str:
    """Crea o aggiorna un file con un commit. Restituisce lo sha del nuovo file.

    sha: quello letto prima di modificare. Se nel frattempo il file è
    cambiato, GitHub rifiuta e nessuna modifica va persa."""
    corpo = {"message": messaggio, "content": base64.b64encode(dati).decode("ascii"), "branch": RAMO}
    if sha:
        corpo["sha"] = sha
    risposta = _chiama("PUT", percorso, corpo)
    return risposta["content"]["sha"]
