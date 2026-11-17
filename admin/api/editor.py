"""Funzione Vercel dell'editor: un solo punto d'ingresso, /api/editor?a=<azione>.

Prima di qualsiasi cosa: token di Cloudflare Access valido ed email ammessa.
Le azioni che cambiano qualcosa vogliono anche POST, JSON e la stessa origine.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

import accesso  # noqa: E402
import azioni   # noqa: E402
import github   # noqa: E402

MAX_CORPO = 4_400_000

LETTURA = {"io", "elenco", "post", "file", "stato"}
SCRITTURA = {"anteprima", "salva", "carica", "nuovo"}

SICUREZZA = {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "DENY",
    "Cross-Origin-Resource-Policy": "same-origin",
}


class handler(BaseHTTPRequestHandler):  # noqa: N801 (nome richiesto da Vercel)

    def _rispondi(self, stato: int, corpo, tipo: str = "application/json; charset=utf-8"):
        dati = corpo if isinstance(corpo, bytes) else json.dumps(corpo, ensure_ascii=False).encode("utf-8")
        self.send_response(stato)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(dati)))
        for k, v in SICUREZZA.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(dati)

    def _utente(self):
        try:
            return accesso.verifica(self.headers.get("Cf-Access-Jwt-Assertion", ""))
        except accesso.Negato as err:
            print("accesso negato:", err)
            return None
        except Exception as err:  # chiavi di Cloudflare non raggiungibili: si resta chiusi
            print("verifica non riuscita:", type(err).__name__)
            return None

    def _azione(self):
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
        return query.get("a", [""])[0], {k: v[0] for k, v in query.items()}

    def do_GET(self):
        azione, q = self._azione()
        email = self._utente()
        if email is None:
            return self._rispondi(401, {"errore": "accesso negato"})
        if azione not in LETTURA:
            return self._rispondi(404, {"errore": "azione sconosciuta"})
        try:
            if azione == "io":
                return self._rispondi(200, {"email": email})
            if azione == "elenco":
                return self._rispondi(*azioni.elenco_post())
            if azione == "post":
                return self._rispondi(*azioni.apri_post(q.get("nome", "")))
            if azione == "stato":
                return self._rispondi(*azioni.stato_pubblicazione(q.get("nome", "")))
            stato, dati, tipo = azioni.file_media(q.get("nome", ""))
            return self._rispondi(stato, dati, tipo)
        except github.ErroreGitHub as err:
            return self._rispondi(err.stato, {"errore": str(err)})
        except Exception as err:
            print("errore:", type(err).__name__, err)
            return self._rispondi(500, {"errore": "errore interno"})

    def do_POST(self):
        azione, _ = self._azione()
        email = self._utente()
        if email is None:
            return self._rispondi(401, {"errore": "accesso negato"})
        if not accesso.stessa_origine(self.headers):
            return self._rispondi(403, {"errore": "richiesta da un'altra pagina"})
        if azione not in SCRITTURA:
            return self._rispondi(404, {"errore": "azione sconosciuta"})
        if not (self.headers.get("Content-Type") or "").startswith("application/json"):
            return self._rispondi(415, {"errore": "serve JSON"})
        try:
            lunghezza = int(self.headers.get("Content-Length") or "0")
        except ValueError:
            lunghezza = -1
        if not 0 < lunghezza <= MAX_CORPO:
            return self._rispondi(413, {"errore": "richiesta troppo grande"})
        try:
            corpo = json.loads(self.rfile.read(lunghezza).decode("utf-8"))
            if not isinstance(corpo, dict):
                raise ValueError
        except (ValueError, UnicodeDecodeError):
            return self._rispondi(400, {"errore": "JSON non valido"})
        try:
            if azione == "nuovo":
                return self._rispondi(*azioni.nuovo(str(corpo.get("titolo", ""))[:120],
                                                    str(corpo.get("data", "")), str(corpo.get("ora", ""))))
            if azione == "anteprima":
                return self._rispondi(*azioni.anteprima(corpo.get("nome"), corpo.get("testo")))
            if azione == "salva":
                print("salvataggio di", corpo.get("nome"))
                return self._rispondi(*azioni.salva(corpo.get("nome"), corpo.get("testo"),
                                                    corpo.get("sha"), email))
            return self._rispondi(*azioni.carica(corpo.get("nome"), corpo.get("dati")))
        except github.ErroreGitHub as err:
            return self._rispondi(err.stato, {"ok": False, "errore": str(err)})
        except ValueError as err:
            return self._rispondi(400, {"ok": False, "errore": str(err)})
        except Exception as err:
            print("errore:", type(err).__name__, err)
            return self._rispondi(500, {"ok": False, "errore": "errore interno"})

    def log_message(self, *args):  # niente log automatici con intestazioni e percorsi
        pass
